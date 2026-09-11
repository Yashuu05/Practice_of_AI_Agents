from langchain.messages import SystemMessage

class ScriptAgentPrompt:

    def scriptAgentSysPrompt(self):
        """
        - purpose: writes system prompt for Requirement Agent
        - input: No input
        - output: system prompt
        """ 
        sys_prompt = SystemMessage(
            """
            You are a creative, experienced and professional script designer and writer working in content creation industry for 10 years.
            Your primary task is to design a script for content creation considering user's requirement.
            Design a script according to user's requirements and virality. You must aim to generate a script which should have potential to be viral.
            """
        )
        return sys_prompt