from transformers import AutoModelForCausalLM, AutoTokenizer
from servers.load_config import Config
import torch


def load_16_bit(config: Config):
    if config.model_path:
        model_path = config.model_path
    else:
        if config.base_model_size == "7b":
            model_path = "eachadea/vicuna-7b-1.1"
        else:
            model_path = "eachadea/vicuna-13b-1.1"

    if config.device == "cpu":
        kwargs = {}
    elif config.device == "cuda":
        kwargs = {"torch_dtype": torch.float16}
        kwargs["device_map"] = "auto"

    print("Loading model: ", model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        low_cpu_mem_usage=True,
        load_in_8bit=(config.use_8bit or config.use_fine_tuned_lora),
        trust_remote_code=True,
        **kwargs
    )
    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)


    if config.use_fine_tuned_lora:
        from peft import PeftModel

        if not config.lora_weights:
            raise ValueError(
                "Provide path to lora weights or set 'use_fine_tuned_lora' to False"
            )
        print("Loading LoRA...")
        model = PeftModel.from_pretrained(
            model,
            config.lora_weights,
            torch_dtype=torch.float16,
        )
        print("LoRA loaded")
        return model,tokenizer

    if config.device == "cuda" and not config.use_8bit:
        model.to(config.device)

    return model, tokenizer
