import gymnasium as gym
import re
from typing import Optional
import numpy as np
import operator
import re

import operator
import re


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


# Example usage

instruction = "if pole_velocity < 0  go left else go right"

# Example usage:


env = gym.make('CartPole-v1',render_mode="human")


observation, info = env.reset()

episode_over = False
inst = "if e.x. || e.y. || e.z. && e.x. + e.y. + e.z. && 0 < e.imag. < 1, go left; else go right;"


while not episode_over:

    print(observation)
    action = interpret_instruction(inst, observation)
    print(action)
    observation, reward, terminated, truncated, info = env.step(action)

    episode_over = terminated or truncated



def control(observation):
    cart_position = observation[0]
    cart_velocity = observation[1]
    pole_angle = observation[2]
    pole_velocity = observation[3]

    if pole_velocity > 0.1:
        return 1
    if pole_velocity < -0.1:
        return 0
    if pole_angle >= 0:
        return 1
    else:
        return 0

while not episode_over:
    action = env.action_space.sample()  # agent policy that uses the observation and info
    action = control(observation)
    observation, reward, terminated, truncated, info = env.step(action)

    episode_over = terminated or truncated

env.close()