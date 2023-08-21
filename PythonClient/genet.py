# import random
#
#
#
# class Member:
#
#     def __init__(self, direction, position, is_wall_on):
#         self.direction = direction
#         self.position = position
#         self.is_wall_on = is_wall_on
#
#
# def generate_first_pop(first_pop_count):
#     res = []
#
#     for i in range(first_pop_count):
#
#     pass
#
# def sort_by_fitness(population):
#
#
# def make_child(parents: list, child_count):
#     children = []
#     for i in range(child_count):
#         child = Member(None, None, False)
#         rand1 = random.randint(0, len(parents) - 1)
#         rand2 = random.randint(0, len(parents) - 1)
#         p1 = parents[rand1]
#         p2 = parents[rand2]
#         child.is_wall_on = p1.is_wall_on
#         child.position = p2.position
#         child.direction = p1.direction
#         children.append(child)
#     return children
