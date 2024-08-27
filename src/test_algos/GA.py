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
DEBUG = True


# Helper function to ensure that the string representation of a float has a certain width
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
        # The highest parcel id is used to determine the maximum value of the genes.
        # The genes are a list of integers that represent the parcels that the agent will deliver.
        # -1 is used to represent the warehouse location.
        self.highest_parcel_id: Id = highest_parcel_id

        # If initialize is True, the DNA will be initialized with a random number of genes
        if initialize:
            num_genes = np.random.randint(1, max_starting_genes)
            self.genes: List[Id] = [self.get_random_genome() for _ in range(num_genes)]
        else:
            self.genes: List[Id] = []

    def get_random_genome(self):
        # -1 is used to represent the warehouse location.
        # highest_parcel_id is the biggest parcel id + 1
        return np.random.randint(-1, self.highest_parcel_id)

    def crossover(self, other: Self, crossover_rate):
        # Crossover the genes of the two agents with a certain probability
        # min length is used to ensure that the crossover is done so that there is no out of bounds errors
        min_length = min(len(self.genes), len(other.genes))
        for i in range(min_length):
            # If the random number is less than the crossover rate, the gene is swapped
            if np.random.rand() < crossover_rate:
                self.genes[i] = other.genes[i]

    def mutate(self, mutation_rate: float):
        # Keep track of the number of genes that are to be removed
        removals = 0
        for i in range(len(self.genes)):
            # Mutate the genes of the agent with a certain probability
            if np.random.rand() < mutation_rate:
                choice = np.random.randint(0, 3)
                if choice == 0:
                    # Randomly change the value of the gene
                    self.genes[i] = self.get_random_genome()
                if choice == 1:
                    # Remove a gene
                    removals += 1
                if choice == 2:
                    # Add a gene
                    self.genes.append(self.get_random_genome())

        # Remove the genes that were marked for removal
        for _ in range(removals):
            choice = np.random.randint(0, len(self.genes))
            self.genes.pop(choice)

        # If the agent has no genes, add a random gene
        if len(self.genes) == 0:
            self.genes.append(self.get_random_genome())

    def copy(self):
        # Create a copy of the agent's DNA
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
        # If initialize is True, the DNA will be initialized with Agents and their genes
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
        # Calculate the fitness of the DNA
        # Allocation is calculated from the DNA
        allocation = {
            agent: gene.genes for agent, gene in zip(self.delivery_agents, self.dna)
        }

        # Simulate the allocation and return the results
        return Simulator(
            allocation, self.delivery_parcels.copy(), self.starting_location
        ).simulate()

    def copy(self):
        # Create a copy of the DNA
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
        # Do the crossover and mutation of the DNA for each agent
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
        # Create a population of DNA
        self.population = [
            DNA(delivery_parcels, delivery_agents, starting_location)
            for _ in range(populations_size)
        ]

        # Set the parameters of the genetic algorithm
        self.population_cutoff = population_cutoff
        self.num_generations = num_generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate

    def solution(self) -> Dict[DeliveryAgentInfo, Route]:
        if DEBUG:
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

        # Run the genetic algorithm for a certain number of generations
        for self.generation_num in range(self.num_generations):
            # Calculate the fitness of the population
            fitness = self.__calculate_fitness()
            # Evolve the population according to the fitness
            self.__evolution(fitness)

        if DEBUG:
            print()

        # Get the best solution from the population. Population top population_cutoffs is sorted by fitness
        winner = self.population[0]

        # Create a dictionary of the solution
        solution = {}
        # Create a mapping of the parcel id to the parcel
        parcel_map = {parcel.id: parcel for parcel in winner.delivery_parcels}

        # Create a dictionary of agents and their routes
        for agent_info, allocation in zip(winner.delivery_agents, winner.dna):
            # Create a route from the allocation
            route: Route = Route([])
            for gene in allocation.genes:
                if gene == -1:
                    route.route.append(None)
                else:
                    route.route.append(parcel_map[gene])

            # Add the route to the solution for the agent
            solution[agent_info] = route

        # Return the solution
        return solution

    def __calculate_fitness(self):
        # Calculate the fitness of the population
        # Get the population size
        pop_size = len(self.population)

        # Create an array to store the information of the population that will be returned from the simulation
        info = np.zeros((pop_size, 3))

        # Calculate the maximum distance that the agents travelled
        max_distance = 0
        no_invalid_agents = 0

        for i, dna in enumerate(self.population):
            # Get the parcels and distance from the simulation when calculating the fitness
            parcels, distance, invalid = dna.calculate_fitness()

            # Track the number of agents that are invalid
            no_invalid_agents += invalid

            # Find the maximum distance that the agents travelled.
            # The multiplication by 1.1 is used to ensure the when normalizing the distances no distance is equal to 1
            max_distance = max(max_distance, distance * 1.1)

            # Store the information of the population
            # First column is the index of the dna in the population
            info[i] = [i, parcels, distance]

        # Normalize the distance of the agents by the maximum distance
        if max_distance != 0:
            info[:, 2] = info[:, 2] / max_distance

        # Calculate the fitness of the population
        fitness = np.zeros((pop_size, 2))
        for i in range(pop_size):
            # The fitness is calculated as the sum of the number of parcels delivered and the distance travelled
            # No of parcels is prioritized over distance therefore it is important that the distance cannot be equal to 1
            # This is achieved by multiplying the max_distance by 1.1 before normalizing
            # A small value is added to make sure that no instance is equal to 0
            fitness[i] = [info[i, 0], info[i, 1] + info[i, 2] + 0.001]

        # Return the sorted fitness
        return fitness[fitness[:, 1].argsort()][::-1]

    def __evolution(self, fitness: np.ndarray):
        new_population = []

        # Calculate the probability of each DNA being selected
        sum_fitness = np.sum(fitness[:, 1])
        # If the sum of the fitness is 0, the probability is set to uniform
        probability = None
        if sum_fitness != 0:
            probability = fitness[:, 1] / sum_fitness

        # Get the indices of the population from the fitness
        indices = fitness[:, 0]

        if DEBUG:
            generation_string = f"{self.generation_num:03}".center(TEXT_CENTER)
            highest_fitness_string = (
                f"{float_ensure_width(fitness[0, 1], TEXT_CENTER - 6)}".center(
                    TEXT_CENTER
                )
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
            # The top population_cutoff DNAs are kept in the new population
            if i < self.population_cutoff:
                new_population.append(self.population[int(indices[i])])
                continue

            # Select two parents based on the probability
            parent1_index = np.random.choice(indices, p=probability)
            parent2_index = np.random.choice(indices, p=probability)

            # First parent is copied since it will be mutated
            # Second parent is not copied since it will not be mutated
            parent1 = self.population[int(parent1_index)].copy()
            parent2 = self.population[int(parent2_index)]

            # Reproduce the parents and add the child to the new population
            new_population.append(
                parent1.reproduce(
                    parent2,
                    self.crossover_rate,
                    self.mutation_rate,
                )
            )
        # Set the population to the new population
        self.population = new_population


def model(
    root_node: Node,
    delivery_parcels: List[Parcel],
    delivery_agents: List[DeliveryAgentInfo],
) -> Dict[DeliveryAgentInfo, Route]:
    # Create a population of DNA and gets the solution
    return Population(delivery_parcels, delivery_agents, root_node).solution()
