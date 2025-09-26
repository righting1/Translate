## LangChain �汾����Ӣ�ķ���ӿڸ������

### ? ����ɵĹ���

1. **���� API �ӿ�**:
   - `POST /api/translate/langchain/zh2en` - LangChain ���ķ���Ӣ��
   - `POST /api/translate/langchain/en2zh` - LangChain Ӣ�ķ�������

2. **�ӿ�����**:
   - �ο� Dedicated �汾��ƣ�ʹ������������������Ӣ�Ļ���
   - ֧��ģ��ѡ�� (`model` ��ѯ����)
   - ֧����ʽ���ÿ��� (`use_chains` ��ѯ����)
   - ʹ�� `SimpleTextRequest` �����ʽ
   - ���� `TranslateResponse` ��Ӧ��ʽ

3. **��������**:
   - �� `test_main.http` ������������Ĳ�������
   - �����������롢��ģ�Ͳ�����������ʽ���õȳ���
   - ������ `test_langchain_routes.py` ��֤�ű�

4. **�ĵ�˵��**:
   - ��������ϸ��ʹ��˵���ĵ�
   - �����ӿڲ�����ʾ�����󡢹������Ե�

### ? �ӿڶԱ�

| ���� | Dedicated �汾 | LangChain �汾 |
|------|----------------|----------------|
| ��Ӣ���� | `/zh2en`, `/en2zh` | `/langchain/zh2en`, `/langchain/en2zh` |
| �����ʽ | `SimpleTextRequest` | `SimpleTextRequest` |
| ��Ӧ��ʽ | `TranslateResponse` | `TranslateResponse` |
| ģ��ѡ�� | ? | ? |
| ��ʽ���� | ? | ? |
| ��� | ֱ�� AI ���� | LangChain ��� |

### ? ʹ��ʾ��

```bash
# ���ķ���Ӣ��
curl -X POST "http://127.0.0.1:8000/api/translate/langchain/zh2en?model=dashscope" \
     -H "Content-Type: application/json" \
     -d '{"text": "��ã����磡"}'

# Ӣ�ķ�������  
curl -X POST "http://127.0.0.1:8000/api/translate/langchain/en2zh" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, world!"}'
```

### ? ��һ��

�������ֱ��ʹ���½ӿڽ��в��ԣ�
1. ��������: `uvicorn main:app --reload`
2. ʹ�� `test_main.http` �еĲ���������֤����
3. ������Ҫ������Ӧ�� AI ģ�� API ��Կ