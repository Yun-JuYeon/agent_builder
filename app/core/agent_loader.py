from google.adk.agents import LlmAgent

def build_agent_from_config(config: dict):
    return LlmAgent(
        name=config["name"],
        model=config["model"],
        tools=config["tools"],
        template=config.get("template", "assistant_agent"),
        max_tokens=config.get("max_tokens", 2000),
        description=config.get("description"),
        instruction=config.get("instruction"),
        temperature=config.get("temperature", 0.7),
    )