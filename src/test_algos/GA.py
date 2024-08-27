from typing import Dict, List, Mapping
from typing_extensions import Self
from common import DeliveryAgentInfo, Parcel, Route, Id
from node import Node

import numpy as np

from simulate import Simulator

MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.5

POPULATION_SIZE = 100
NUM_GENERATIONS = 100

POPULATION_CUTOFF = 10

TEXT_CENTER = 25


def float_ensure_width(value: float, width: int) -> str:
    value_part = str(int(value))
    width -= len(value_part) + 1
    width = max(width, 0)

    return f"{value:.{width}f}"


class AgentDNA:
    def __init__(
        self,
        highest_parcel_id: int,
        max_starting_genes: int,
        initialize=True,
    ):
        self.highest_parcel_id: Id = highest_parcel_id
        if initialize:
            num_genes = np.random.randint(1, max_starting_genes)
            self.genes: List[Id] = [self.get_random_genome() for _ in range(num_genes)]
        else:
            self.genes: List[Id] = []

    def get_random_genome(self):
        return np.random.randint(-1, self.highest_parcel_id)

    def crossover(self, other: Self, crossover_rate):
        min_length = min(len(self.genes), len(other.genes))
        for i in range(min_length):
            if np.random.rand() < crossover_rate:
                self.genes[i] = other.genes[i]

    def mutate(self, mutation_rate: float):
        removals = 0
        for i in range(len(self.genes)):
            if np.random.rand() < mutation_rate:
                choice = np.random.randint(0, 3)
                if choice == 0:
                    self.genes[i] = self.get_random_genome()
                if choice == 1:
                    removals += 1
                if choice == 2:
                    self.genes.append(self.get_random_genome())

        for _ in range(removals):
            choice = np.random.randint(0, len(self.genes))
            self.genes.pop(choice)

        if len(self.genes) == 0:
            self.genes.append(self.get_random_genome())

    def copy(self):
        other = AgentDNA(self.highest_parcel_id, 0, False)
        other.genes = self.genes.copy()
        return other


class DNA:
    def __init__(
        self,
        delivery_parcels: List[Parcel],
        delivery_agents: List[DeliveryAgentInfo],
        starting_location: Node,
        initialize: bool = True,
    ):
        if initialize:
            self.dna: List[AgentDNA] = [
                AgentDNA(len(delivery_parcels), 2 * agent.max_capacity)
                for agent in delivery_agents
            ]
        else:
            self.dna: List[AgentDNA] = []
        self.delivery_agents = delivery_agents
        self.delivery_parcels = delivery_parcels
        self.starting_location = starting_location

    def calculate_fitness(self):
        allocation = {
            agent: gene.genes for agent, gene in zip(self.delivery_agents, self.dna)
        }
        return Simulator(
            allocation, self.delivery_parcels.copy(), self.starting_location
        ).simulate()

    def copy(self):
        other = DNA(
            self.delivery_parcels,
            self.delivery_agents,
            self.starting_location,
            False,
        )
        for i in range(len(self.dna)):
            other.dna.append(self.dna[i].copy())
        return other

    def reproduce(self, other: Self, crossover_rate, mutation_rate):
        for i in range(len(self.dna)):
            self.dna[i].crossover(other.dna[i], crossover_rate)
            self.dna[i].mutate(mutation_rate)
            # Enforce that the stariing location is always the first gene
            self.dna[i].genes[0] = -1
        return self


class Population:
    def __init__(
        self,
        delivery_parcels: List[Parcel],
        delivery_agents: List[DeliveryAgentInfo],
        starting_location: Node,
        populations_size: int = POPULATION_SIZE,
        num_generations: int = NUM_GENERATIONS,
        population_cutoff: int = POPULATION_CUTOFF,
        crossover_rate: float = CROSSOVER_RATE,
        mutation_rate: float = MUTATION_RATE,
    ):
        self.population = [
            DNA(delivery_parcels, delivery_agents, starting_location)
            for _ in range(populations_size)
        ]
        self.population_cutoff = population_cutoff
        self.num_generations = num_generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate

    def solution(self) -> Dict[DeliveryAgentInfo, Route]:
        print("=" * 79)
        print(" GA Progress:")
        print("-" * 79)
        print(
            "|"
            + "Generation No".center(TEXT_CENTER)
            + "|"
            + "Highest Fitness".center(TEXT_CENTER)
            + "|"
            + "Average Fitness".center(TEXT_CENTER)
            + "|"
        )
        print("-" * 79)

        for self.generation_num in range(self.num_generations):
            fitness = self.__calculate_fitness()
            self.__evolution(fitness)

        print()

        winner = self.population[0]
        solution = {}
        parcel_map = {parcel.id: parcel for parcel in winner.delivery_parcels}

        for agent_info, allocation in zip(winner.delivery_agents, winner.dna):
            route: Route = Route([])
            for gene in allocation.genes:
                if gene == -1:
                    route.route.append(None)
                else:
                    route.route.append(parcel_map[gene])

            solution[agent_info] = route
        return solution

    def __calculate_fitness(self):
        pop_size = len(self.population)
        info = np.zeros((pop_size, 3))
        max_distance = 0
        no_invalid_agents = 0

        for i, dna in enumerate(self.population):
            parcels, distance, invalid = dna.calculate_fitness()
            no_invalid_agents += invalid

            max_distance = max(max_distance, distance * 1.1)
            info[i] = [i, parcels, distance]

        if max_distance != 0:
            info[:, 2] = info[:, 2] / max_distance

        fitness = np.zeros((pop_size, 2))
        for i in range(pop_size):
            fitness[i] = [info[i, 0], info[i, 1] + info[i, 2] + 0.001]

        return fitness[fitness[:, 1].argsort()][::-1]

    def __evolution(self, fitness: np.ndarray):
        new_population = []

        probability = None
        sum_fitness = np.sum(fitness[:, 1])
        if sum_fitness != 0:
            probability = fitness[:, 1] / sum_fitness

        indices = fitness[:, 0]

        generation_string = f"{self.generation_num:03}".center(TEXT_CENTER)
        highest_fitness_string = (
            f"{float_ensure_width(fitness[0, 1], TEXT_CENTER - 6)}".center(TEXT_CENTER)
        )
        average_fitness_string = f"{float_ensure_width(fitness[len(self.population)//2, 1], TEXT_CENTER - 6)}".center(
            TEXT_CENTER
        )
        print(
            "\r|"
            + generation_string
            + "|"
            + highest_fitness_string
            + "|"
            + average_fitness_string
            + "|",
            end="",
        )
        for i in range(len(self.population)):
            if i < self.population_cutoff:
                new_population.append(self.population[int(indices[i])])
                continue

            parent1_index = np.random.choice(indices, p=probability)
            parent2_index = np.random.choice(indices, p=probability)

            parent1 = self.population[int(parent1_index)].copy()
            parent2 = self.population[int(parent2_index)]
            new_population.append(
                parent1.reproduce(
                    parent2,
                    self.crossover_rate,
                    self.mutation_rate,
                )
            )
        self.population = new_population


def model(
    root_node: Node,
    delivery_parcels: List[Parcel],
    delivery_agents: List[DeliveryAgentInfo],
) -> Dict[DeliveryAgentInfo, Route]:
    return Population(delivery_parcels, delivery_agents, root_node).solution()
