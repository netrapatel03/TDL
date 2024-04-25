def calculate_sus_score(answers):
    # Calculate individual score contributions for questions 1, 3, 5, 7, and 9
    positive_sum = sum(answers[i] - 1 for i in [0, 2, 4, 6, 8])
    
    # Calculate individual score contributions for questions 2, 4, 6, 8, and 10
    negative_sum = sum(5 - answers[i] for i in [1, 3, 5, 7, 9])
    
    # Calculate raw SUS score
    raw_score = positive_sum + negative_sum
    
    # Calculate final SUS score
    sus_score = raw_score * 2.5
    
    return sus_score

def sus():
    # Define SUS questions
    questions = [
        "   ",
        "The gameplay using hand gestures is challenging.",
        "I find the gameplay engaging.",
        "The hand gesture recognition system works accurately.",
        "The in-game instructions are helpful.",
        "I find it easy to understand how to play the game.",
        "Hand gesture controls are beneficial for individuals with Parkinson's disease.",
        "I experienced difficulties with hand gesture recognition.",
        "I enjoy playing the game using hand gestures.",
        "I feel confident using the game with hand gestures."
    ]
    
    # Initialize an empty list to store user responses
    answers = []
    
    # Prompt the user to input their responses for each question
    print("Please provide your responses for the following questions:")
    for i, question in enumerate(questions, start=1):
        print(f"\nQuestion {i}: {question}")
        answer = int(input("Enter your response (1 to 5): "))
        
        # Ensure the response is within the range of 1 to 5
        while answer < 1 or answer > 5:
            print("Invalid response. Please enter a number between 1 and 5.")
            answer = int(input("Enter your response (1 to 5): "))
        
        answers.append(answer)
    
    # Calculate and display the SUS score
    sus_score = calculate_sus_score(answers)
    print("\nSUS Score:", sus_score)