import json5


class HistoryMemory:
    def __init__(self, previous_trace: list = [], reflection: str = "") -> None:
        self.previous_trace = previous_trace
        self.reflection = reflection

    def stringfy_thought_and_action(self) -> str:
        input_list = None
        str_output = ""
        try:
            input_list = json5.loads(self.previous_trace, encoding="utf-8")
        except:
            input_list = self.previous_trace
        if len(input_list) > 2:
            str_output = "["
            for idx in range(len(input_list)-1):
                str_output += f'Step{idx+1}:\"Thought: {input_list[idx]["thought"]}, Action: {input_list[idx]["action"]}, Reflection: {input_list[idx+1]["reflection"]}\";\n'
            str_output += "]"
            current_trace = input_list[-1]
            str_output += f'Specifically in the last step, you gave the following Thought: {current_trace["thought"]}\n You performed the following Action: {current_trace["action"]}\n You had the following Reflection: {self.reflection}\";\n'
        else:
            current_trace = input_list[-1]
            str_output += f'Specifically in the last step, you gave the following Thought: {current_trace["thought"]}\n You performed the following Action: {current_trace["action"]}\n You had the following Reflection: {self.reflection}\";\n'
        return str_output

    def construct_previous_trace_prompt(self) -> str:
        stringfy_thought_and_action_output = self.stringfy_thought_and_action()
        previous_trace_prompt = f"The previous thoughts, actions and reflections are as follows: \
            {stringfy_thought_and_action_output}.\n\nYou have done the things above.\n\n"
        return previous_trace_prompt

    @staticmethod
    def construct_cache(cache_info: list, max_steps: int = 5):
        """Build a simple cache from a list of interaction steps.

        Parameters
        ----------
        cache_info : list
            Sequence of dictionaries describing previous steps.
        max_steps : int, optional
            Maximum number of recent steps to keep, by default 5.

        Returns
        -------
        list
            Trimmed list containing the most recent steps.
        """

        if not isinstance(cache_info, list):
            raise ValueError("cache_info must be a list")
        if max_steps <= 0:
            raise ValueError("max_steps must be positive")

        return cache_info[-max_steps:]
