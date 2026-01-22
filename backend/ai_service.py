import json
import re
import os
from openai import OpenAI
from typing import Dict, Any, List, Optional

# DeepSeek API 配置 - 从环境变量读取
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

if not DEEPSEEK_API_KEY:
    print("WARNING: DEEPSEEK_API_KEY environment variable not set!")
    print("Please set it in backend/.env file or system environment variables")

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


def is_single_word(text: str) -> bool:
    """判断输入是否为单个单词"""
    text = text.strip()
    # 移除标点符号
    clean_text = re.sub(r"[^\w\s-]", "", text)
    words = clean_text.split()
    return len(words) == 1


def analyze_word(word: str) -> Dict[str, Any]:
    """分析单个单词"""
    prompt = f"""Analyze the English word "{word}" and return a JSON object with the following structure:
{{
    "word": "{word}",
    "part_of_speech": "noun/verb/adjective/etc.",
    "definition": "Clear and concise English definition",
    "collocations": ["common collocation 1", "common collocation 2", "common collocation 3"],
    "example_sentence": "A sentence example in tech/business/analytical context"
}}

Keep the response strictly as JSON. Make the definition simple and practical. Focus on tech/business contexts."""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "You are an English learning assistant. Always respond with valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        if response.choices and response.choices[0] and response.choices[0].message:
            result_text = response.choices[0].message.content or ""
            result_text = result_text.strip()
            # 提取 JSON（如果被包裹在代码块中）
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            return json.loads(result_text)
        else:
            raise Exception("Invalid response from API")
    except Exception as e:
        print(f"Error analyzing word: {e}")
        # 返回默认结构
        return {
            "word": word,
            "part_of_speech": "unknown",
            "definition": f"Definition for {word}",
            "collocations": [],
            "example_sentence": f"Example with {word}.",
        }


def analyze_sentence(sentence: str) -> Dict[str, Any]:
    """分析句子"""
    prompt = f"""Analyze the following English sentence and return a JSON object with this structure:
{{
    "sentence": "{sentence}",
    "function": "What is the communicative function? (e.g., emphasizing, contrasting, explaining, expressing opinion)",
    "pattern": "What is the sentence pattern or expression structure?",
    "why_good": "Why is this a good sentence? (brief)",
    "rewrite_examples": ["Example rewrite 1", "Example rewrite 2"]
}}

Sentence to analyze: "{sentence}"

Keep the response strictly as JSON. Focus on what makes this sentence useful for learning and how the pattern can be reused."""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "You are an English learning assistant focusing on sentence patterns and expressions. Always respond with valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=800,
        )

        if response.choices and response.choices[0] and response.choices[0].message:
            result_text = response.choices[0].message.content or ""
            result_text = result_text.strip()
            # 提取 JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            return json.loads(result_text)
        else:
            raise Exception("Invalid response from API")
    except Exception as e:
        print(f"Error analyzing sentence: {e}")
        return {
            "sentence": sentence,
            "function": "unknown",
            "pattern": "N/A",
            "why_good": "Analysis failed",
            "rewrite_examples": [],
        }


def generate_embedding(text: str) -> List[float]:
    """生成文本的 embedding 向量"""
    try:
        # DeepSeek 可能没有 embedding API，我们用 text 模型生成一个简化的表示
        # 或者使用其他方法。这里我们先用一个简化的实现
        # 在实际中，可以考虑使用 sentence-transformers 或其他本地模型

        # 临时方案：使用字符级别的简单哈希向量（仅用于 MVP）
        # 在生产环境中应该使用专门的 embedding 模型
        import hashlib

        # 生成一个 384 维的简化向量
        hash_obj = hashlib.sha384(text.encode())
        hash_bytes = hash_obj.digest()

        # 将字节转换为浮点数向量
        embedding = []
        for i in range(0, len(hash_bytes), 3):
            chunk = hash_bytes[i : i + 3]
            value = int.from_bytes(chunk + b"\x00" * (3 - len(chunk)), "big")
            embedding.append(value / (256**3))  # 归一化到 0-1

        # 确保是 384 维
        while len(embedding) < 384:
            embedding.append(0.0)

        return embedding[:384]
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # 返回零向量
        return [0.0] * 384


def analyze_content(
    content: str, source: Optional[str] = None, note: Optional[str] = None
) -> Dict[str, Any]:
    """
    分析内容（单词或句子）
    返回结构：
    {
        "entry_type": "word" or "sentence",
        "analysis": {...},
        "tags": ["tag1", "tag2"]
    }
    """
    content = content.strip()

    if is_single_word(content):
        entry_type = "word"
        analysis = analyze_word(content)
        # 生成标签
        tags = [analysis.get("part_of_speech", ""), "vocabulary"]
    else:
        entry_type = "sentence"
        analysis = analyze_sentence(content)
        # 生成标签
        function = analysis.get("function", "")
        tags = [entry_type, function.split()[0] if function else "expression"]

    # 添加来源作为标签
    if source:
        tags.append((source or "").lower())

    # 清理标签
    tags = [t.strip() for t in tags if t and t.strip()]

    return {"entry_type": entry_type, "analysis": analysis, "tags": tags}
