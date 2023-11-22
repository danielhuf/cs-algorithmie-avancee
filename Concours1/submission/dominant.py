import sys, os, time
import networkx as nx

def calculate_score(D1, D2, g):
    # The operation return (len(D1) + len(D2) + len(list(set(D1) & set(D2)))) / len(g.nodes()) can be slow for large graphs

    common_nodes = 0
    d1_set = set(D1)
    for node in D2:
        if node in d1_set:
            common_nodes += 1

    return (len(D1) + len(D2) + common_nodes) / len(g.nodes())

def is_dominant_set(g, d):
    for node in g.nodes:
        if node not in d and not any(neighbor in d for neighbor in g.neighbors(node)):
            return False
    return True

def calculate_D1(node, g):
    D1_test = []
    g_temp = g.copy()

    # Greedy algorithm: while there are still nodes in the graph, pick the node with highest degree and remove it and its neighbors from the graph
    while g_temp.nodes:
        D1_test.append(node)
        for neighbor in list(g_temp.neighbors(node)):
            g_temp.remove_node(neighbor)
        g_temp.remove_node(node)
        if g_temp.nodes:
            node, _ = max(g_temp.degree, key=lambda x: x[1])
    return D1_test

def calculate_D2(node, g, D1):
    # Begin by adding the node with highest degree to D2 and removing it and its neighbors from a copy of the graph
    D2_test = [node]
    g_temp = g.copy()
    for neighbor in list(g_temp.neighbors(node)):
        g_temp.remove_node(neighbor)
    g_temp.remove_node(node)

    # Modified greedy algorithm 
    while g_temp.nodes:
        nodes_excluding_D1 = [n for n in g_temp.nodes if n not in D1]
        # pick node with highest degree in 'g_temp' as long as it does not belong to D1
        if nodes_excluding_D1:
            max_node = max(nodes_excluding_D1, key=lambda n: g_temp.degree(n))
        # else, nodes that belong to D1 can be picked
        else:
            max_node, _ = max(g_temp.degree, key=lambda x: x[1])

        D2_test.append(max_node)
        for neighbor in list(g_temp.neighbors(max_node)):
            g_temp.remove_node(neighbor)
        g_temp.remove_node(max_node)
    return D2_test

def find_longest_path(graph):
    def dfs(node, visited, current_path):
        visited.add(node)
        current_path.append(node)
        longest = current_path.copy()
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                path = dfs(neighbor, visited, current_path)
                if len(path) > len(longest):
                    longest = path
        
        current_path.pop()
        visited.remove(node)
        return longest

    longest_path = []
    visited_nodes = set()

    for node in graph.nodes():
        if node not in visited_nodes:
            path = dfs(node, visited_nodes, [])
            if len(path) > len(longest_path):
                longest_path = path

    return longest_path

def dominant(g):
    """
        A Faire:
        - Ecrire une fonction qui retourne deux dominants du graphe non dirigé g passé en parametre.
        - Cette fonction doit retourner une liste contenant deux sous-listes. Les sous-listes sont les noeuds des dominants D1 et D2.
        - Le score est (|D1| + |D2| + |D1 inter D2|) / |V|, où |V| est le nombre de noeuds du graphe.
        - Ce score doit être minimal.
        - La pondération des sommets n'a pas d'importance pour le calcul du score.

        :param g: le graphe est donné dans le format networkx : https://networkx.github.io/documentation/stable/reference/classes/graph.html

    """

    # Special case: if the number of nodes is equal to the number of edges, we can simply pick every other node in the longest path of g and split them into D1 and D2
    if len(g.nodes()) == len(g.edges()):
        # Create a list of nodes that are present in the longest path of g
        longest_path = find_longest_path(g)
        # Pick the nodes 0, 3, 6, 9, ... from the longest path and add them to D1
        D1 = [longest_path[i] for i in range(0, len(longest_path), 3)]
        # Pick the nodes 1, 4, 7, 10, ... from the longest path and add them to D2
        D2 = [longest_path[i] for i in range(1, len(longest_path), 3)]
        # Add the last node to D2
        if longest_path[-1] not in D2:
            D2.append(longest_path[-1])
        if is_dominant_set(g, D1) and is_dominant_set(g, D2):
            return [D1, D2]

    D1 = []
    D2 = []

    # Calculate D1 25 times, each one starting with a different node from the 25 nodes with highest degree
    best_nodes = sorted(g.degree, key=lambda x: x[1], reverse=True)[:25]
    D1_trials = []
    for node, _ in best_nodes:
        D1_trials.append(calculate_D1(node, g))

    # Pick the D1 with the smallest length
    D1 = min(D1_trials, key=lambda x: len(x))

    # Calculate D2 25 times, each one starting with a different node from the 25 nodes with highest degree (excluding nodes that appear in D1)
    g_temp = g.copy()
    g_temp.remove_nodes_from(D1)
    best_nodes = sorted(g_temp.degree, key=lambda x: x[1], reverse=True)[:25]
    D2_trials = []
    for node, _ in best_nodes:
        D2_trials.append(calculate_D2(node, g, D1))

    # Pick the D2 with the smallest score
    best_score = 3
    for trial in D2_trials:
        score = calculate_score(D1, trial, g)
        if score < best_score:
            D2 = trial
            best_score = score

    return [D1, D2]

#########################################
#### Ne pas modifier le code suivant ####
#########################################


def load_graph(name):
    with open(name, "r") as f:
        state = 0
        G = None
        for l in f:
            if state == 0:  # Header nb of nodes
                state = 1
            elif state == 1:  # Nb of nodes
                nodes = int(l)
                state = 2
            elif state == 2:  # Header position
                i = 0
                state = 3
            elif state == 3:  # Position
                i += 1
                if i >= nodes:
                    state = 4
            elif state == 4:  # Header node weight
                i = 0
                state = 5
                G = nx.Graph()
            elif state == 5:  # Node weight
                G.add_node(i, weight=int(l))
                i += 1
                if i >= nodes:
                    state = 6
            elif state == 6:  # Header edge
                i = 0
                state = 7
            elif state == 7:
                if i > nodes:
                    pass
                else:
                    edges = l.strip().split(" ")
                    for j, w in enumerate(edges):
                        w = int(w)
                        if w == 1 and (not i == j):
                            G.add_edge(i, j)
                    i += 1

        return G


#########################################
#### Ne pas modifier le code suivant ####
#########################################
if __name__ == "__main__":
    start_time = time.time()
    input_dir = os.path.abspath(sys.argv[1])
    output_dir = os.path.abspath(sys.argv[2])

    # un repertoire des graphes en entree doit être passé en parametre 1
    if not os.path.isdir(input_dir):
        print(input_dir, "doesn't exist")
        exit()

    # un repertoire pour enregistrer les dominants doit être passé en parametre 2
    if not os.path.isdir(output_dir):
        print(output_dir, "doesn't exist")
        exit()

        # fichier des reponses depose dans le output_dir et annote par date/heure
    output_filename = 'answers_{}.txt'.format(time.strftime("%d%b%Y_%H%M%S", time.localtime()))
    output_file = open(os.path.join(output_dir, output_filename), 'w')

    score = 0

    print('Graph - Score - D1 - D2')
    for graph_filename in sorted(os.listdir(input_dir)):
        # importer le graphe
        g = load_graph(os.path.join(input_dir, graph_filename))

        # calcul du dominant
        d1, d2 = dominant(g)
        D1 = sorted(d1, key=lambda x: int(x))
        D2 = sorted(d2, key=lambda x: int(x))

        # ajout au rapport
        output_file.write(graph_filename)
        for node in D1:
            output_file.write(' {}'.format(node))
        output_file.write('-')
        for node in D2:
            output_file.write(' {}'.format(node))
        output_file.write('\n')

        # calculate final score
        s = calculate_score(D1, D2, g)
        print('{} : {} : {} : {}'.format(graph_filename, s, is_dominant_set(g, d1), is_dominant_set(g, d2)))
        score += s

    output_file.close()
    end_time = time.time()
    print('Final score: {}'.format(score))
    print('Execution time:', end_time - start_time, "seconds")
'''if __name__ == "__main__":
    input_dir = os.path.abspath(sys.argv[1])
    output_dir = os.path.abspath(sys.argv[2])

    # un repertoire des graphes en entree doit être passé en parametre 1
    if not os.path.isdir(input_dir):
        print(input_dir, "doesn't exist")
        exit()

    # un repertoire pour enregistrer les dominants doit être passé en parametre 2
    if not os.path.isdir(output_dir):
        print(input_dir, "doesn't exist")
        exit()

        # fichier des reponses depose dans le output_dir et annote par date/heure
    output_filename = 'answers_{}.txt'.format(time.strftime("%d%b%Y_%H%M%S", time.localtime()))
    output_file = open(os.path.join(output_dir, output_filename), 'w')

    for graph_filename in sorted(os.listdir(input_dir)):
        # importer le graphe
        g = load_graph(os.path.join(input_dir, graph_filename))

        # calcul du dominant
        d1, d2 = dominant(g)
        D1 = sorted(d1, key=lambda x: int(x))
        D2 = sorted(d2, key=lambda x: int(x))

        # ajout au rapport
        output_file.write(graph_filename)
        for node in D1:
            output_file.write(' {}'.format(node))
        output_file.write('-')
        for node in D2:
            output_file.write(' {}'.format(node))
        output_file.write('\n')

    output_file.close()'''