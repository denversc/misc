# See https://xon.sh/tutorial.html#customizing-the-prompt

from dconeybe.xonsh import prompt as dconeybe_prompt

prompt = dconeybe_prompt.Prompt($HOSTNAME)
$PROMPT_FIELDS["time_format"] = prompt.time_format()
$PROMPT = prompt.prompt()
$RIGHT_PROMPT = prompt.right_prompt()

del prompt, dconeybe_prompt
