def construct_prompt(has_reference):
    """Construct the prompt for the Gemini API based on uploaded files."""
    prompt = (
        "You are an expert at evaluating university exam answer sheets. "
        "I will provide you with a question paper and an answer sheet. "
    )
    
    if has_reference:
        prompt += (
            "I will also provide a reference answer sheet which you should use as a guide. "
            "Compare the student's answers with the reference answers."
        )
    
    prompt += (
        "For each question, provide:\n"
        "1. An evaluation of the correctness of the answer (as a percentage)\n"
        "2. Marks to be awarded out of the allocated marks\n"
        "3. Explanation of what is correct and what is incorrect\n\n"
        "Format your analysis as a table with columns: Question Number, Marks Allocated, "
        "Percentage of Correct Content, Marks Awarded, Comments\n\n"
        "Be precise and educational in your feedback."
    )
    
    return prompt