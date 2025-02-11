import re
import random
import ast
import operator
import gymnasium as gym
from typing import Optional


def parse_condition(condition, observation):
    ops = {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne
    }

    variables = {
        "cart_position": observation[0],
        "cart_velocity": observation[1],
        "pole_angle": observation[2],
        "pole_velocity": observation[3]
    }

    condition = re.split(r'[;]', condition)[0].strip()  # Remove additional comments or text
    if not any(var in condition for var in variables):
        return False  # If no recognized variables are in the condition, treat it as meaningless

    for op in ops.keys():
        if op in condition:
            try:
                var, value = re.split(r'\s*' + re.escape(op) + r'\s*', condition)
                var = var.strip()
                value = re.sub(r'[^0-9.-]', '', value.strip())  # Remove non-numeric characters from value
                value = float(value)
                if var in variables and ops[op](variables[var], value):
                    return True
            except (ValueError, IndexError):
                return False  # Handle cases where condition format is invalid
    return False


def interpret_instruction(instruction, observation):
    if 'go right' in instruction and 'if' not in instruction:
        return 1
    if 'go left' in instruction and 'if' not in instruction:
        return 0

    match = re.findall(r'if (.+?) go (left|right)(?: else go (left|right))?', instruction)
    if match:
        for condition, direction, else_direction in match:
            conditions = condition.split(' and ')
            if all(parse_condition(cond, observation) for cond in conditions):
                return 0 if direction == 'left' else 1
            elif else_direction:
                return 0 if else_direction == 'left' else 1

    return 1  # Default action changed to right if no conditions match or instruction is meaningless

def extract_solution(solution_str):
    """Extract the equation from the solution string."""
    # Remove everything before the first "Assistant:"
    if "Assistant:" in solution_str:
        solution_str = solution_str.split("Assistant:", 1)[1]
    elif "<|im_start|>assistant" in solution_str:
        solution_str = solution_str.split("<|im_start|>assistant", 1)[1]
    else:
        return None
    solution_str = solution_str.split('\n')[-1]

    answer_pattern = r'<answer>(.*?)</answer>'
    match = re.finditer(answer_pattern, solution_str)
    matches = list(match)
    if matches:
        final_answer = matches[-1].group(1).strip()
    else:
        final_answer = None

    print("FINAL ANSWER")
    print(final_answer)
    print("FINAL ANSWER")
    return final_answer


def validate_equation(equation_str, available_numbers):
    """Validate that equation only uses available numbers and each number once."""
    try:
        # Extract all numbers from the equation
        numbers_in_eq = [int(n) for n in re.findall(r'\d+', equation_str)]

        # Check if all numbers in equation are available
        available_numbers = sorted(available_numbers)
        numbers_in_eq = sorted(numbers_in_eq)

        # Each number should be used exactly once
        return numbers_in_eq == available_numbers
    except:
        return False


def evaluate_equation(equation_str):

    env = gym.make('CartPole-v1')
    observation, info = env.reset()
    episode_over = False
    reward = 0
    while not episode_over:

        action = interpret_instruction(equation_str, observation)
        observation, rew, terminated, truncated, info = env.step(action)
        reward +=rew
        episode_over = terminated or truncated
    return reward/50

def sevaluate_equation(equation_str):
    """Safely evaluate the arithmetic equation using eval() with precautions."""
    try:
        # Define a regex pattern that only allows numbers, operators, parentheses, and whitespace
        allowed_pattern = r'^[\d+\-*/().\s]+$'
        if not re.match(allowed_pattern, equation_str):
            raise ValueError("Invalid characters in equation.")

        # Evaluate the equation with restricted globals and locals
        result = eval(equation_str, {"__builtins__": None}, {})
        return result
    except Exception as e:
        return None


def compute_score(solution_str, ground_truth, method='strict', format_score=0.1, score=1.):
    """The scoring function for countdown task.

    Args:
        solution_str: the solution text
        ground_truth: dictionary containing target number and available numbers
        method: the method to extract the solution
        format_score: the score for correct format but wrong answer
        score: the score for the correct answer
    """

    target = ground_truth['target']
    numbers = ground_truth['numbers']

    equation = extract_solution(solution_str=solution_str)
    do_print = random.randint(1, 64) == 1

    if do_print:
        print(f"--------------------------------")
        print(f"Target: {target} | Numbers: {numbers}")
        print(f"Extracted equation: {equation}")
        print(f"Solution string: {solution_str}")

    if equation is None:
        if do_print:
            print(f"No equation found")
        return 0
    else:
        print("\n" * 5)
        print("TESTING GYM")
        print(equation)
        print("\n" * 5)

        result = evaluate_equation(equation)
        return result

    # Validate equation uses correct numbers
    if not validate_equation(equation, numbers):
        if do_print:
            print(f"Invalid equation")
        return format_score

    # Evaluate equation
    try:
        print("TESTING GYM")
        result = evaluate_equation(equation)
        return result
        '''
        if result is None:
            if do_print:
                print(f"Could not evaluate equation")
            return format_score

        if abs(result - target) < 1e-5:  # Account for floating point precision
            if do_print:
                print(f"Correct equation: {equation} = {result}")
            return score
        else:
            if do_print:
                print(f"Wrong result: equation = {result}, target = {target}")
            return format_score
        '''
    except:
        if do_print:
            print(f"Error evaluating equation")
        return format_score