import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, AutoTokenizer

from peft import LoraConfig, get_peft_model, PeftModel

lr_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=[
        "query_key_value",
        "dense",
        "dense_h_to_4h",
        "dense_4h_to_h",
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

peft_model = PeftModel.from_pretrained(model, model_id='/Users/galen/Documents/clone/falcon-7b-peft', config=lr_config)

merged_model = peft_model.merge_and_unload()

# save the model to disk
merged_model.save_pretrained("./falcon-7b-peft-merged")

with torch.no_grad():
    with open("some.txt", "r", encoding="utf-8") as f:
        prompt = f.read()

    input_ids = tokenizer.encode(prompt, return_tensors='pt')
    input_ids = input_ids.to(model.device)
    print(input_ids.shape)
    # take the last 1600 tokens
    input_ids = input_ids[:, -2000:]
    print(input_ids.shape)
    output = model.generate(input_ids=input_ids, max_new_tokens=100, do_sample=True, temperature=0.9)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    print(generated_text)
