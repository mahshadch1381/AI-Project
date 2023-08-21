# -*- coding: utf-8 -*-

# python imports
#  random

import copy
import math
import random

# chillin imports
from chillin_client import RealtimeAI

# project imports
from ks.models import ECell, EDirection, Position
from ks.commands import ChangeDirection, ActivateWallBreaker

table = []
parents_count = 10
child_count = 5
pm = 15
x = math.inf
c = -math.inf
side_my = ""


class Member:

    def __init__(self, direction, position, is_wall_on):
        self.direction = direction
        self.position = position
        self.is_wall_on = is_wall_on
        self.fitness = 0


class Action:
    def __init__(self, direction, wall):
        self.direction = direction
        self.wall = wall


class AI(RealtimeAI):

    def __init__(self, world):
        super(AI, self).__init__(world)

    def initialize(self):
        print('initialize')

    def decide(self):
        print('decide')
        global table
        table = self.world.board
        temp_word = copy.deepcopy(self.world)
        global side_my
        side_my = self.my_side
        action = self.min_max_dec(temp_word)
        if action is not None:
            if action.wall:
                self.send_command(ActivateWallBreaker())
        self.send_command(ChangeDirection(action.direction))

    def min_max_dec(self, state):
        iteration = 5
        v = self.max_val1(state, -math.inf, math.inf, iteration)
        return v

    def max_val1(self, state, alpha, beta, iteration):
        v = -math.inf
        actions = self.available_actions(state, True)
        selected_action = None
        for i in actions:
            copystate = copy.deepcopy(state)
            resul, isdone = self.result(copystate, i, True)
            c = self.min_val(resul, isdone, alpha, beta, iteration)
            if c >= v:
                v = c
                selected_action = i
            if v >= beta:
                return selected_action
            self.chrcking_genetic(selected_action, v)
            alpha = max(alpha, v)

        return selected_action

    def max_val(self, state, isdone, alpha, beta, iteration):
        if iteration == 0:
            return self.utility_calc(state)
        v = -math.inf
        actions = self.available_actions(state, True)
        iteration = iteration - 1
        if isdone:
            return math.inf
        for i in actions:
            copystate = copy.deepcopy(state)
            resul, issdone = self.result(copystate, i, True)
            v = max(v, self.min_val(resul, issdone, alpha, beta, iteration))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_val(self, state, isDone, alpha, beta, iteration):
        if iteration == 0:
            return self.utility_calc(state)
        v = math.inf
        actions = self.available_actions(state, False)
        iteration = iteration - 1
        if isDone:
            return -math.inf
        for i in actions:
            copystate = copy.deepcopy(state)
            resul, isddone = self.result(copystate, i, False)
            v = min(v, self.max_val(resul, isddone, alpha, beta, iteration))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    def utility_calc(self, state):
        my_health = state.agents[self.my_side].health
        other_health = state.agents[self.other_side].health
        my_score = state.scores[self.my_side]
        other_score = state.scores[self.other_side]
        delta = my_score - other_score
        res = ((my_score + 10) + delta) * my_health * my_health
        return res

    def result(self, state, action: Action, our_side):
        direction = action.direction
        make_wall_on = action.wall
        colored_wall = None
        IsDone = False
        global x
        if self.my_side == "Yellow":
            colored_wall = ECell.YellowWall
        else:
            colored_wall = ECell.BlueWall
        if our_side:
            if state.agents[self.my_side].wall_breaker_rem_time > 0:
                state.agents[self.my_side].wall_breaker_rem_time -= 1

            if state.agents[self.my_side].wall_breaker_cooldown > 0:
                state.agents[self.my_side].wall_breaker_cooldown -= 1

            if make_wall_on:
                state.agents[self.my_side].wall_breaker_rem_time = self.world.constants.wall_breaker_duration

            state.board[state.agents[self.my_side].position.y][state.agents[self.my_side].position.x] = colored_wall
            state.scores[self.my_side] += 1

            if direction == EDirection.Down:
                state.agents[self.my_side].position.y = state.agents[self.my_side].position.y + 1
                state.agents[self.my_side].direction = EDirection.Down

            if direction == EDirection.Up:
                state.agents[self.my_side].position.y = state.agents[self.my_side].position.y - 1
                state.agents[self.my_side].direction = EDirection.Up

            if direction == EDirection.Right:
                state.agents[self.my_side].position.x = state.agents[self.my_side].position.x + 1
                state.agents[self.my_side].direction = EDirection.Right

            if direction == EDirection.Left:
                state.agents[self.my_side].position.x = state.agents[self.my_side].position.x - 1
                state.agents[self.my_side].direction = EDirection.Left

            if state.board[state.agents[self.my_side].position.y][
                state.agents[self.my_side].position.x] == ECell.AreaWall:
                IsDone = True
                state.scores[self.my_side] = -100
                return state, IsDone
            if (state.board[state.agents[self.my_side].position.y][
                state.agents[self.my_side].position.x] == ECell.YellowWall):
                state.scores["Yellow"] -= 20

            if (state.board[state.agents[self.my_side].position.y][
                state.agents[self.my_side].position.x] == ECell.BlueWall):
                state.scores["Blue"] -= 20

            if state.agents[self.my_side].wall_breaker_rem_time == 0:  # if wall breaker is off
                if not (state.board[state.agents[self.my_side].position.y][
                            state.agents[self.my_side].position.x] == ECell.Empty):
                    state.agents[self.my_side].health -= 1
                    if state.agents[self.my_side].health == 0:
                        if self.my_side == "Blue" and state.board[state.agents[self.my_side].position.y][
                            state.agents[self.my_side].position.x] == ECell.BlueWall:
                            state.scores[self.my_side] -= state.constants.my_wall_crash_score
                        if self.my_side == "Yellow" and state.board[state.agents[self.my_side].position.y][
                            state.agents[self.my_side].position.x] == ECell.YellowWall:
                            state.scores[self.my_side] -= state.constants.my_wall_crash_score
                        if self.my_side == "Blue" and state.board[state.agents[self.my_side].position.y][
                            state.agents[self.my_side].position.x] == ECell.YellowWall:
                            state.scores[self.my_side] -= state.constants.enemy_wall_crash_score
                        if self.my_side == "Yellow" and state.board[state.agents[self.my_side].position.y][
                            state.agents[self.my_side].position.x] == ECell.BlueWall:
                            state.scores[self.my_side] -= state.constants.enemy_wall_crash_score
                        IsDone = True




        else:
            if state.agents[self.other_side].wall_breaker_rem_time > 0:
                state.agents[self.other_side].wall_breaker_rem_time -= 1

            if state.agents[self.other_side].wall_breaker_cooldown > 0:
                state.agents[self.other_side].wall_breaker_cooldown -= 1

            if make_wall_on:
                state.agents[self.other_side].wall_breaker_rem_time = self.world.constants.wall_breaker_duration

            state.board[state.agents[self.other_side].position.y][
                state.agents[self.other_side].position.x] = colored_wall
            state.scores[self.other_side] += 1

            if direction == EDirection.Down:
                state.agents[self.other_side].position.y = state.agents[self.other_side].position.y + 1
                state.agents[self.other_side].direction = EDirection.Down
            if direction == EDirection.Up:
                state.agents[self.other_side].position.y = state.agents[self.other_side].position.y - 1
                state.agents[self.other_side].direction = EDirection.Up
            if direction == EDirection.Right:
                state.agents[self.other_side].position.x = state.agents[self.other_side].position.x + 1
                state.agents[self.other_side].direction = EDirection.Right
            x = c
            if direction == EDirection.Left:
                state.agents[self.other_side].position.x = state.agents[self.other_side].position.x - 1
                state.agents[self.other_side].direction = EDirection.Left
            if state.board[state.agents[self.other_side].position.y][
                state.agents[self.other_side].position.x] == ECell.AreaWall:
                IsDone = True
                state.scores[self.other_side] = -100
                return state, IsDone
            if (state.board[state.agents[self.other_side].position.y][
                state.agents[self.other_side].position.x] == ECell.YellowWall):
                state.scores["Yellow"] -= 3
            if (state.board[state.agents[self.other_side].position.y][
                state.agents[self.other_side].position.x] == ECell.BlueWall):
                state.scores["Blue"] -= 3

            if state.agents[self.other_side].wall_breaker_rem_time == 0:  # if wall breaker is off
                if not (state.board[state.agents[self.other_side].position.y][
                            state.agents[self.other_side].position.x] == ECell.Empty):
                    state.agents[self.other_side].health -= 1
                    if state.agents[self.other_side].health == 0:
                        if self.other_side == "Blue" and state.board[state.agents[self.other_side].position.y][
                            state.agents[self.other_side].position.x] == ECell.BlueWall:
                            state.scores[self.other_side] -= state.constants.my_wall_crash_score
                        if self.other_side == "Yellow" and state.board[state.agents[self.other_side].position.y][
                            state.agents[self.other_side].position.x] == ECell.YellowWall:
                            state.scores[self.other_side] -= state.constants.my_wall_crash_score
                        if self.other_side == "Blue" and state.board[state.agents[self.other_side].position.y][
                            state.agents[self.other_side].position.x] == ECell.YellowWall:
                            state.scores[self.other_side] -= state.constants.enemy_wall_crash_score
                        if self.other_side == "Yellow" and state.board[state.agents[self.other_side].position.y][
                            state.agents[self.other_side].position.x] == ECell.BlueWall:
                            state.scores[self.other_side] -= state.constants.enemy_wall_crash_score
                        IsDone = True
        return state, IsDone

    def chrcking_genetic(self, v, utility):
        if utility < x:
            action = self.genetic()
            if action.fitness > utility:
                v.direction = action.direction
                return v
        return v

    def available_actions(self, current_word, our_side):
        res = []
        is_wall_on = False
        down_available = False
        up_available = False
        left_available = False
        right_available = False
        if our_side:
            if current_word.agents[self.my_side].position.y + 1 < len(self.world.board) - 1:
                if not (current_word.board[current_word.agents[self.my_side].position.y][
                            current_word.agents[self.my_side].position.x] == ECell.AreaWall):
                    down_available = True
            if current_word.agents[self.my_side].position.y - 1 > 0:
                up_available = True
            if current_word.agents[self.my_side].position.x + 1 < len(self.world.board[0]) - 1:
                right_available = True
            if current_word.agents[self.my_side].position.x - 1 > 0:
                left_available = True
            direction = current_word.agents[self.my_side].direction
            if current_word.agents[self.my_side].wall_breaker_rem_time > 0:
                is_wall_on = True

            if direction == EDirection.Up:
                if is_wall_on:
                    if up_available:
                        a1 = Action(EDirection.Up, False)
                        res.append(a1)
                    if right_available:
                        a2 = Action(EDirection.Right, False)
                        res.append(a2)
                    if left_available:
                        a3 = Action(EDirection.Left, False)
                        res.append(a3)

                else:
                    if current_word.agents[self.my_side].wall_breaker_cooldown > 0:
                        if up_available:
                            a1 = Action(EDirection.Up, False)
                            res.append(a1)
                        if right_available:
                            a2 = Action(EDirection.Right, False)
                            res.append(a2)
                        if left_available:
                            a3 = Action(EDirection.Left, False)
                            res.append(a3)

                    else:
                        if up_available:
                            a1 = Action(EDirection.Up, False)
                            a11 = Action(EDirection.Up, True)
                            res.append(a1)
                            res.append(a11)
                        if right_available:
                            a2 = Action(EDirection.Right, False)
                            a22 = Action(EDirection.Right, True)
                            res.append(a2)
                            res.append(a22)
                        if left_available:
                            a3 = Action(EDirection.Left, False)
                            a33 = Action(EDirection.Left, True)
                            res.append(a3)
                            res.append(a33)

            if direction == EDirection.Down:
                if is_wall_on:
                    if down_available:
                        a1 = Action(EDirection.Down, False)
                        res.append(a1)
                    if right_available:
                        a2 = Action(EDirection.Right, False)
                        res.append(a2)
                    if left_available:
                        a3 = Action(EDirection.Left, False)
                        res.append(a3)

                else:
                    if current_word.agents[self.my_side].wall_breaker_cooldown > 0:
                        if down_available:
                            a1 = Action(EDirection.Down, False)
                            res.append(a1)
                        if right_available:
                            a2 = Action(EDirection.Right, False)
                            res.append(a2)
                        if left_available:
                            a3 = Action(EDirection.Left, False)
                            res.append(a3)

                    else:
                        if down_available:
                            a1 = Action(EDirection.Down, False)
                            a11 = Action(EDirection.Down, True)
                            res.append(a1)
                            res.append(a11)
                        if right_available:
                            a2 = Action(EDirection.Right, False)
                            a22 = Action(EDirection.Right, True)
                            res.append(a2)
                            res.append(a22)
                        if left_available:
                            a3 = Action(EDirection.Left, False)
                            a33 = Action(EDirection.Left, True)
                            res.append(a3)
                            res.append(a33)

            if direction == EDirection.Left:
                if is_wall_on:
                    if down_available:
                        a1 = Action(EDirection.Down, False)
                        res.append(a1)
                    if up_available:
                        a2 = Action(EDirection.Up, False)
                        res.append(a2)
                    if left_available:
                        a3 = Action(EDirection.Left, False)
                        res.append(a3)

                else:
                    if current_word.agents[self.my_side].wall_breaker_cooldown > 0:
                        if down_available:
                            a1 = Action(EDirection.Down, False)
                            res.append(a1)
                        if up_available:
                            a2 = Action(EDirection.Up, False)
                            res.append(a2)
                        if left_available:
                            a3 = Action(EDirection.Left, False)
                            res.append(a3)

                    else:
                        if down_available:
                            # print("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
                            a1 = Action(EDirection.Down, False)
                            a11 = Action(EDirection.Down, True)
                            res.append(a1)
                            res.append(a11)
                        if up_available:
                            a2 = Action(EDirection.Up, False)
                            a22 = Action(EDirection.Up, True)
                            res.append(a2)
                            res.append(a22)
                        if left_available:
                            a3 = Action(EDirection.Left, False)
                            a33 = Action(EDirection.Left, True)
                            res.append(a3)
                            res.append(a33)

            if direction == EDirection.Right:

                if is_wall_on:
                    if down_available:
                        a1 = Action(EDirection.Down, False)
                        res.append(a1)
                    if up_available:
                        a2 = Action(EDirection.Up, False)
                        res.append(a2)
                    if right_available:
                        a3 = Action(EDirection.Right, False)
                        res.append(a3)

                else:
                    if current_word.agents[self.my_side].wall_breaker_cooldown > 0:
                        if down_available:
                            a1 = Action(EDirection.Down, False)
                            res.append(a1)
                        if up_available:
                            a2 = Action(EDirection.Up, False)
                            res.append(a2)
                        if right_available:
                            a3 = Action(EDirection.Right, False)
                            res.append(a3)

                    else:
                        if down_available:
                            a1 = Action(EDirection.Down, False)
                            a11 = Action(EDirection.Down, True)
                            res.append(a1)
                            res.append(a11)
                        if up_available:
                            a2 = Action(EDirection.Up, False)
                            a22 = Action(EDirection.Up, True)
                            res.append(a2)
                            res.append(a22)
                        if right_available:
                            a3 = Action(EDirection.Right, False)
                            a33 = Action(EDirection.Right, True)
                            res.append(a3)
                            res.append(a33)

        else:
            res = []
            is_wall_on = False
            down_available = False
            up_available = False
            left_available = False
            right_available = False
            if current_word.agents[self.other_side].position.y + 1 < len(self.world.board) - 1:
                down_available = True
            if current_word.agents[self.other_side].position.y - 1 > 0:
                up_available = True
            if current_word.agents[self.other_side].position.x + 1 < len(self.world.board[0]) - 1:
                right_available = True
            if current_word.agents[self.other_side].position.x - 1 > 0:
                left_available = True
            direction = self.world.agents[self.other_side].direction
            if current_word.agents[self.other_side].wall_breaker_rem_time > 0:
                is_wall_on = True

            if direction == EDirection.Up:
                if is_wall_on:
                    if up_available:
                        a1 = Action(EDirection.Up, False)
                        res.append(a1)
                    if right_available:
                        a2 = Action(EDirection.Right, False)
                        res.append(a2)
                    if left_available:
                        a3 = Action(EDirection.Left, False)
                        res.append(a3)

                else:
                    if current_word.agents[self.other_side].wall_breaker_cooldown > 0:
                        if up_available:
                            a1 = Action(EDirection.Up, False)
                            res.append(a1)
                        if right_available:
                            a2 = Action(EDirection.Right, False)
                            res.append(a2)
                        if left_available:
                            a3 = Action(EDirection.Left, False)
                            res.append(a3)

                    else:
                        if up_available:
                            a1 = Action(EDirection.Up, False)
                            a11 = Action(EDirection.Up, True)
                            res.append(a1)
                            res.append(a11)
                        if right_available:
                            a2 = Action(EDirection.Right, False)
                            a22 = Action(EDirection.Right, True)
                            res.append(a2)
                            res.append(a22)
                        if left_available:
                            a3 = Action(EDirection.Left, False)
                            a33 = Action(EDirection.Left, True)
                            res.append(a3)
                            res.append(a33)

            if direction == EDirection.Down:
                if is_wall_on:
                    if down_available:
                        a1 = Action(EDirection.Down, False)
                        res.append(a1)
                    if right_available:
                        a2 = Action(EDirection.Right, False)
                        res.append(a2)
                    if left_available:
                        a3 = Action(EDirection.Left, False)
                        res.append(a3)

                else:
                    if current_word.agents[self.other_side].wall_breaker_cooldown > 0:
                        if down_available:
                            a1 = Action(EDirection.Down, False)
                            res.append(a1)
                        if right_available:
                            a2 = Action(EDirection.Right, False)
                            res.append(a2)
                        if left_available:
                            a3 = Action(EDirection.Left, False)
                            res.append(a3)

                    else:
                        if down_available:
                            a1 = Action(EDirection.Down, False)
                            a11 = Action(EDirection.Down, True)
                            res.append(a1)
                            res.append(a11)
                        if right_available:
                            a2 = Action(EDirection.Right, False)
                            a22 = Action(EDirection.Right, True)
                            res.append(a2)
                            res.append(a22)
                        if left_available:
                            a3 = Action(EDirection.Left, False)
                            a33 = Action(EDirection.Left, True)
                            res.append(a3)
                            res.append(a33)

            if direction == EDirection.Left:
                if is_wall_on:
                    if down_available:
                        a1 = Action(EDirection.Down, False)
                        res.append(a1)
                    if up_available:
                        a2 = Action(EDirection.Up, False)
                        res.append(a2)
                    if left_available:
                        a3 = Action(EDirection.Left, False)
                        res.append(a3)

                else:
                    if current_word.agents[self.other_side].wall_breaker_cooldown > 0:
                        if down_available:
                            a1 = Action(EDirection.Down, False)
                            res.append(a1)
                        if up_available:
                            a2 = Action(EDirection.Up, False)
                            res.append(a2)
                        if left_available:
                            a3 = Action(EDirection.Left, False)
                            res.append(a3)

                    else:
                        if down_available:
                            a1 = Action(EDirection.Down, False)
                            a11 = Action(EDirection.Down, True)
                            res.append(a1)
                            res.append(a11)
                        if up_available:
                            a2 = Action(EDirection.Up, False)
                            a22 = Action(EDirection.Up, True)
                            res.append(a2)
                            res.append(a22)
                        if left_available:
                            a3 = Action(EDirection.Left, False)
                            a33 = Action(EDirection.Left, True)
                            res.append(a3)
                            res.append(a33)

            if direction == EDirection.Right:
                if is_wall_on:
                    if down_available:
                        a1 = Action(EDirection.Down, False)
                        res.append(a1)
                    if up_available:
                        a2 = Action(EDirection.Up, False)
                        res.append(a2)
                    if right_available:
                        a3 = Action(EDirection.Right, False)
                        res.append(a3)

                else:
                    if current_word.agents[self.other_side].wall_breaker_cooldown > 0:
                        if down_available:
                            a1 = Action(EDirection.Down, False)
                            res.append(a1)
                        if up_available:
                            a2 = Action(EDirection.Up, False)
                            res.append(a2)
                        if right_available:
                            a3 = Action(EDirection.Right, False)
                            res.append(a3)
                    else:
                        if down_available:
                            a1 = Action(EDirection.Down, False)
                            a11 = Action(EDirection.Down, True)
                            res.append(a1)
                            res.append(a11)
                        if up_available:
                            a2 = Action(EDirection.Up, False)
                            a22 = Action(EDirection.Up, True)
                            res.append(a2)
                            res.append(a22)
                        if right_available:
                            a3 = Action(EDirection.Right, False)
                            a33 = Action(EDirection.Right, True)
                            res.append(a3)
                            res.append(a33)

        return res

    def generate_first_pop(self, first_pop_count):
        res = []
        dict = {0: EDirection.Up, 1: EDirection.Down, 2: EDirection.Left, 3: EDirection.Right}
        m1 = Member(self.world.agents[self.my_side].direction, self.world.agents[self.my_side].position,
                    self.world.agents[self.my_side].wall_breaker_rem_time)
        res.append(m1)
        for i in range(first_pop_count - 1):
            x = random.randint(0, len(self.world.board[0]))
            y = random.randint(0, len(self.world.board))
            position = Position(x, y)
            num = random.randint(0, 3)
            direction = dict[num]
            onoff = random.randint(0, 1)
            if onoff:
                onnn = True
            else:
                onnn = False
            m2 = Member(position, direction, onnn)
            res.append(m2)
            return res

    def select_parents(self, sorted_population):
        parents = sorted_population[:parents_count]
        return parents

    def fitness(self, mem: Member):
        res = []
        is_wall_on = False
        down_available = False
        up_available = False
        left_available = False
        right_available = False
        if self.world.agents[self.my_side].position.y + 1 < len(self.world.board) - 1:
            down_available = True
        if self.world.agents[self.my_side].position.y - 1 > 0:
            up_available = True
        if self.world.agents[self.my_side].position.x + 1 < len(self.world.board[0]) - 1:
            right_available = True
        if self.world.agents[self.my_side].position.x - 1 > 0:
            left_available = True
        direction = self.world.agents[self.my_side].direction
        if self.world.agents[self.my_side].wall_breaker_rem_time > 0:
            is_wall_on = True

        if direction == EDirection.Up:
            if is_wall_on:
                if up_available:
                    a1 = Action(EDirection.Up, False)
                    res.append(a1)
                if right_available:
                    a2 = Action(EDirection.Right, False)
                    res.append(a2)
                if left_available:
                    a3 = Action(EDirection.Left, False)
                    res.append(a3)

            else:
                if self.world.agents[self.my_side].wall_breaker_cooldown > 0:
                    if up_available:
                        a1 = Action(EDirection.Up, False)
                        res.append(a1)
                    if right_available:
                        a2 = Action(EDirection.Right, False)
                        res.append(a2)
                    if left_available:
                        a3 = Action(EDirection.Left, False)
                        res.append(a3)

                else:
                    if up_available:
                        a1 = Action(EDirection.Up, False)
                        a11 = Action(EDirection.Up, True)
                        res.append(a1)
                        res.append(a11)
                    if right_available:
                        a2 = Action(EDirection.Right, False)
                        a22 = Action(EDirection.Right, True)
                        res.append(a2)
                        res.append(a22)
                    if left_available:
                        a3 = Action(EDirection.Left, False)
                        a33 = Action(EDirection.Left, True)
                        res.append(a3)
                        res.append(a33)

        if direction == EDirection.Down:
            if is_wall_on:
                if down_available:
                    a1 = Action(EDirection.Down, False)
                    res.append(a1)
                if right_available:
                    a2 = Action(EDirection.Right, False)
                    res.append(a2)
                if left_available:
                    a3 = Action(EDirection.Left, False)
                    res.append(a3)

            else:
                if self.world.agents[self.my_side].wall_breaker_cooldown > 0:
                    if down_available:
                        a1 = Action(EDirection.Down, False)
                        res.append(a1)
                    if right_available:
                        a2 = Action(EDirection.Right, False)
                        res.append(a2)
                    if left_available:
                        a3 = Action(EDirection.Left, False)
                        res.append(a3)

                else:
                    if down_available:
                        a1 = Action(EDirection.Down, False)
                        a11 = Action(EDirection.Down, True)
                        res.append(a1)
                        res.append(a11)
                    if right_available:
                        a2 = Action(EDirection.Right, False)
                        a22 = Action(EDirection.Right, True)
                        res.append(a2)
                        res.append(a22)
                    if left_available:
                        a3 = Action(EDirection.Left, False)
                        a33 = Action(EDirection.Left, True)
                        res.append(a3)
                        res.append(a33)

        if direction == EDirection.Left:
            if is_wall_on:
                if down_available:
                    a1 = Action(EDirection.Down, False)
                    res.append(a1)
                if up_available:
                    a2 = Action(EDirection.Up, False)
                    res.append(a2)
                if left_available:
                    a3 = Action(EDirection.Left, False)
                    res.append(a3)

            else:
                if self.world.agents[self.my_side].wall_breaker_cooldown > 0:
                    if down_available:
                        a1 = Action(EDirection.Down, False)
                        res.append(a1)
                    if up_available:
                        a2 = Action(EDirection.Up, False)
                        res.append(a2)
                    if left_available:
                        a3 = Action(EDirection.Left, False)
                        res.append(a3)

                else:
                    if down_available:
                        a1 = Action(EDirection.Down, False)
                        a11 = Action(EDirection.Down, True)
                        res.append(a1)
                        res.append(a11)
                    if up_available:
                        a2 = Action(EDirection.Up, False)
                        a22 = Action(EDirection.Up, True)
                        res.append(a2)
                        res.append(a22)
                    if left_available:
                        a3 = Action(EDirection.Left, False)
                        a33 = Action(EDirection.Left, True)
                        res.append(a3)
                        res.append(a33)

        if direction == EDirection.Right:

            if is_wall_on:
                if down_available:
                    a1 = Action(EDirection.Down, False)
                    res.append(a1)
                if up_available:
                    a2 = Action(EDirection.Up, False)
                    res.append(a2)
                if right_available:
                    a3 = Action(EDirection.Right, False)
                    res.append(a3)

            else:
                if self.world.agents[self.my_side].wall_breaker_cooldown > 0:
                    if down_available:
                        a1 = Action(EDirection.Down, False)
                        res.append(a1)
                    if up_available:
                        a2 = Action(EDirection.Up, False)
                        res.append(a2)
                    if right_available:
                        a3 = Action(EDirection.Right, False)
                        res.append(a3)

                else:
                    if down_available:
                        a1 = Action(EDirection.Down, False)
                        a11 = Action(EDirection.Down, True)
                        res.append(a1)
                        res.append(a11)
                    if up_available:
                        a2 = Action(EDirection.Up, False)
                        a22 = Action(EDirection.Up, True)
                        res.append(a2)
                        res.append(a22)
                    if right_available:
                        a3 = Action(EDirection.Right, False)
                        a33 = Action(EDirection.Right, True)
                        res.append(a3)
                        res.append(a33)
        max_score = 0
        max_health = 0
        for action in res:
            if direction == EDirection.Down:
                mem.position.y = mem.position.position.y + 1
                mem.direction = EDirection.Down

            if direction == EDirection.Up:
                mem.position.y = mem.position.y - 1
                mem.direction = EDirection.Up

            if direction == EDirection.Right:
                mem.position.x = mem.position.x + 1
                mem.direction = EDirection.Right

            if direction == EDirection.Left:
                mem.position.x = mem.position.x - 1
                mem.direction = EDirection.Left
            score = 0
            health = 3
            wall_flag = False
            for i in range(2):
                if table[mem.position.x][mem.position.y] == ECell.AreaWall:
                    score -= 40
                if mem.is_wall_on or wall_flag:
                    score += 1
                if side_my == "Yellow" and table[mem.position.x][mem.position.y] == ECell.YellowWall:
                    score -= 1
                if side_my == "Blue" and table[mem.position.x][mem.position.y] == ECell.BlueWall:
                    score -= 1
                if side_my == "Yellow" and table[mem.position.x][mem.position.y] == ECell.BlueWall:
                    score += 1
                if side_my == "Blue" and table[mem.position.x][mem.position.y] == ECell.YellowWall:
                    score += 1

                else:
                    if action.wall:
                        if side_my == "Yellow" and table[mem.position.x][mem.position.y] == ECell.YellowWall:
                            score -= 1
                        if side_my == "Blue" and table[mem.position.x][mem.position.y] == ECell.BlueWall:
                            score -= 1
                        if side_my == "Yellow" and table[mem.position.x][mem.position.y] == ECell.BlueWall:
                            score += 1
                        if side_my == "Blue" and table[mem.position.x][mem.position.y] == ECell.YellowWall:
                            score += 1
                        score += 1
                        wall_flag = True
                    else:
                        score += 1
                        if not table[mem.position.y][mem.position.x] == ECell.Empty:
                            score -= 1
                            health -= 1
                    if score >= max_score and health >= max_health:
                        max_score = score
                        max_score = health

                return (max_score + 10) + max_health * max_health

    def sort_by_fitness(self, population):
        fits = []
        for i in population:
            fit = self.fitness(i)
            fits.append(fit)
            i.fitness = fit
        population.sort(key=lambda x: x.fitness, reverse=True)
        return population

    def make_child(self, parents: list, child_count):
        children = []
        Pmake_child = 0.9
        for i in range(child_count):
            child = Member(None, None, False)
            rand1 = random.randint(0, len(parents) - 1)
            rand2 = random.randint(0, len(parents) - 1)
            p1 = parents[rand1]
            p2 = parents[rand2]
            num = random.random()
            if num < Pmake_child:
                child.is_wall_on = p1.is_wall_on
                child.position = p2.position
                child.direction = p1.direction
                children.append(child)
        return children

    def make_mutation(self, children):
        for child in children:
            rand1 = random.randint(0, 100)
            if rand1 < pm:
                dict = {0: EDirection.Up, 1: EDirection.Down, 2: EDirection.Left, 3: EDirection.Right}
                num = random.randint(0, 3)
                direction = dict[num]
                child.direction = direction
        return children

    def delete_and_add(self, childern, first_population: list, best):
        i = 0
        while i < len(childern):
            index = random.randint(0, 15 - 1)
            if first_population[i] == best:
                continue
            first_population.pop(index)
            first_population.insert(index, childern[i])
            i = i + 1

    def genetic(self):
        first_population = self.generate_first_pop(15)
        best = None
        for i in range(100):
            after_sort = self.sort_by_fitness(first_population)
            best = after_sort[0]
            parents = self.select_parents(after_sort)
            children = self.make_child(parents, child_count)
            after_mutation = self.make_mutation(children)
            self.delete_and_add(after_mutation, first_population, best)
        return best
