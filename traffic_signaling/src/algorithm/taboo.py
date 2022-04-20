from random import randint

from algorithm.common import distributed_sum_permutation, generate_random_solution, mutate_intersection, mutate_schedule
from model.city import City


def taboo_search(city: City, number_of_iterations: int, number_of_mutations_per_iteration: int, max_worse_jump_percentage=0.1):
    first_solution = generate_random_solution(
        city, distributed_sum_permutation)
    current = first_solution, first_solution.evaluate(city)
    avg_score = current[1]
    current_max = current
    taboo_memory = {intersection_no: 0 for intersection_no in range(
        city.no_intersections)}
    improvement_to_max = 0
    for i in range(number_of_iterations):
        mutations = []
        mutated, tries = 0, 0
        while mutated < number_of_mutations_per_iteration:
            candidate, mutated_intersection = mutate_intersection(
                city, current[0])
            if tries > 100 or taboo_memory[mutated_intersection.id] <= 0:
                mutations.append(
                    (candidate, mutated_intersection, candidate.evaluate(city)))
                mutated += 1
                tries = 0
            tries += 1
        taboo_memory = {intersection_id: max(
            0, taboo_memory[intersection_id]-1) for intersection_id in taboo_memory}
        best_candidate = max(mutations, key=lambda x: x[2])
        current = (best_candidate[0], best_candidate[2])
        taboo_memory[best_candidate[1].id] = randint(
            0, (number_of_iterations - i) // 2)
        improvement_to_max = current[1] - current_max[1]
        if improvement_to_max > 0:
            current_max = current
        else:
            if -improvement_to_max > avg_score//(1/max_worse_jump_percentage):
                current = current_max
        print(current[1])
    return current_max
