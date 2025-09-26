# LangChain ��Ӣ�ķ���ӿڸ���˵��

## ����
���θ���Ϊ������������ר�ŵ� LangChain ��Ӣ�ķ���ӿڣ��ο� Dedicated �汾����ƣ�ʹ��������������������Ӣ�Ļ��෭�롣

## �����ӿ�

### 1. LangChain ���ķ����Ӣ��
- **URL**: `POST /api/translate/langchain/zh2en`
- **����**: ʹ�� LangChain ��ܽ����ķ����Ӣ��
- **������**: `SimpleTextRequest`
- **��ѯ����**:
  - `model` (��ѡ): AIģ������
  - `use_chains` (��ѡ): �Ƿ�ʹ��Ԥ����������Ĭ��Ϊ `true`

#### ʾ������
```http
POST http://127.0.0.1:8000/api/translate/langchain/zh2en?model=dashscope
Content-Type: application/json

{
  "text": "��ã����磡����һ��ʹ��LangChain��ܵķ�����ԡ�"
}
```

### 2. LangChain Ӣ�ķ��������
- **URL**: `POST /api/translate/langchain/en2zh`
- **����**: ʹ�� LangChain ��ܽ�Ӣ�ķ��������
- **������**: `SimpleTextRequest`
- **��ѯ����**:
  - `model` (��ѡ): AIģ������
  - `use_chains` (��ѡ): �Ƿ�ʹ��Ԥ����������Ĭ��Ϊ `true`

#### ʾ������
```http
POST http://127.0.0.1:8000/api/translate/langchain/en2zh?model=dashscope
Content-Type: application/json

{
  "text": "Hello, world! This is a translation test using LangChain framework."
}
```

## ��Ӧ��ʽ
�����ӿڶ����� `TranslateResponse` ��ʽ��

```json
{
  "translated_text": "������",
  "source_language": "����",
  "target_language": "Ӣ��",
  "result": "������",
  "model": "ʹ�õ�ģ������"
}
```

## ��������

### 1. ��ʽ����֧��
- Ĭ��ʹ��Ԥ������ LangChain �� (`use_chains=true`)
- ���Խ�����ʽ����ʹ��ֱ��ģʽ (`use_chains=false`)

### 2. ģ��ѡ��
- ֧��ͨ�� `model` ��ѯ����ָ�� AI ģ��
- ֧�ֵ�ģ��: `dashscope`, `openai`, `zhipuai`, `ollama`, `azure`
- �����ָ��ģ�ͣ�ʹ��Ĭ�ϵ� `langchain_default`

### 3. ������
- �������쳣����ʹ��󷵻�
- ��ϸ�Ĵ�����־��¼
- HTTP 500 ״̬���ʾ����������

## �����нӿڵ�����

### �� Dedicated �ӿڵıȽ�
- **���Ƶ�**: 
  - ʹ����ͬ������/��Ӧ��ʽ (`SimpleTextRequest`/`TranslateResponse`)
  - �ṩר�ŵ���Ӣ�ķ���ӿ�
  - ֧��ģ��ѡ��
  
- **��ͬ��**:
  - LangChain �汾֧����ʽ���� (`use_chains` ����)
  - LangChain �汾ʹ�� LangChain ��ܵĸ߼�����
  - ·��ǰ׺Ϊ `/langchain/` �����ְ汾

### ��ͨ�� LangChain �ӿڵıȽ�
- **ͨ�ýӿ�**: `/api/translate/langchain/translate` - ��Ҫָ��Ŀ������
- **ר�Žӿ�**: `/api/translate/langchain/zh2en`, `/api/translate/langchain/en2zh` - �̶����뷽��

## ��������
�� `test_main.http` �ļ�������������Ĳ���������

1. **�����������**
2. **��ģ�Ͳ����ķ������**  
3. **������ʽ���õķ������**

## ʹ�ý���

### 1. �����Ż�
- ����Ƶ������Ӣ�ķ��룬����ʹ����ʽ���� (`use_chains=true`)
- ����ʵ���Է��룬���Խ�����ʽ���ò��Բ�ͬ����

### 2. ģ��ѡ��
- `dashscope`: �Ƽ��������ķ��룬Ч���Ϻ�
- `openai`: �ʺϸ��������룬����Ҫ API ��Կ
- `zhipuai`: ����ģ�ͣ��ʺ����Ĵ���

### 3. ������
- ʼ�ռ����Ӧ״̬��
- ������ܵ����糬ʱ��ģ�ͷ��񲻿������

## ����Ҫ��

ȷ�� `config.yaml` ����������Ӧ�� AI ģ�ͷ���

```yaml
ai_models:
  dashscope:
    api_key: "your_dashscope_api_key"
    base_url: "https://dashscope.aliyuncs.com/api/v1"
    model: "qwen-turbo"
  # ... ����ģ������
```

## ��һ���ƻ�

1. **���ܼ��**: ��ӷ����������ٶȼ��
2. **�������**: ʵ�ַ���������
3. **��������**: ֧�������ı�����
4. **�Զ�����ʾ**: ֧���û��Զ��巭����ʾģ��