import sys, os, time
# pour lire un dictionnaire d'un fichier
import ast
# pour faire la statistique
import statistics, numpy
# pour verifier si une solution online traite toutes les tâches
import collections
# pour utiliser random, si besoin est
import random
import math

# -------------------------------------------------------------- #
# --------------------- Variables globales --------------------- #
# -------------------------------------------------------------- #

global fast_speed, sol_online # sol_online permet de consulter l'état de machines en cours de traitement

# la vitesse des machines rapides est toujours unitaire
fast_speed=1


# -------------------------------------------------------------- #
# --- Fonctions utilitaires - n'y touchez pas, les enfants ! --- #
# -------------------------------------------------------------- #

def val_sol(sigma, m, fast_nb, slow_speed, sol):
    load = []
    for machine in sol[:fast_nb]:
        load_machine = sum(machine)*fast_speed
        load.append(load_machine)
    for machine in sol[fast_nb:]:
        load_machine = sum(machine)*slow_speed
        load.append(load_machine)
    return max(load)

def verify_solution(sigma, sol):
    # applatir la solution online pour pouvoir la comparer avec sigma
    attributed_to_machines = [job for machine in sol for job in machine]
    if not collections.Counter(attributed_to_machines) == collections.Counter(sigma):
        print("Solution incompléte")
        exit

def mon_algo_est_deterministe():
    # par défaut l'algo est considéré comme déterministe
    # changez response = False dans le cas contraire
    response = True #False #True 
    return response 

##############################################################
# La fonction à completer pour la compétition
##############################################################

def slow_fast_scheduling_online(sol_online, m, fast_nb, slow_speed, job):
    """
        À faire:         
        - Écrire une fonction qui attribue une tâche courante à une machine
        le résultat est répertorié dans une variable globale sol_online, liste de listes de durées de tâches
  
    """
    # ###############################
    # complétez cette fonction en choisissant un sous-enseble couvrant l'élément courant el
    # ###############################
    
    # Calculate average job size
    if all([not machine for machine in sol_online]):
        avg_job = 0
    else:
        total_jobs = sum([sum(machine) for machine in sol_online])
        avg_job = total_jobs / sum([len(machine) for machine in sol_online])

    # Calculate average workload for fast and slow machines
    avg_workload_fast = sum([sum(machine) * fast_speed for machine in sol_online[:fast_nb]]) / fast_nb if fast_nb != 0 else 0
    avg_workload_slow = sum([sum(machine) * slow_speed for machine in sol_online[fast_nb:]]) / (m - fast_nb) if m - fast_nb != 0 else 0

    # Adjust threshold based on the workload difference
    dynamic_factor = avg_workload_fast / (avg_workload_slow + 0.00001)  # added 0.00001 to avoid division by zero
    threshold = avg_job * dynamic_factor

    # Workload of the fast machines
    work_left_fast_machines = [(sum(machine) + job) * fast_speed for machine in sol_online[:fast_nb]]

    # Workload of the slow machines
    work_left_slow_machines = [(sum(machine) + job) * slow_speed for machine in sol_online[fast_nb:]]

    # Least Work Left Heuristic
    min_work_left_machine_index_fast = work_left_fast_machines.index(min(work_left_fast_machines))
    min_work_left_machine_index_slow = work_left_slow_machines.index(min(work_left_slow_machines)) + fast_nb

    # Adaptive threshold
    if job > threshold:
        # Assign job direcly to a fast machine if it is bigger than the threshold
        sol_online[min_work_left_machine_index_fast].append(job)
    elif job < 0.3 * threshold:
        # Assign job direcly to a slow machine if it is smaller than the threshold multiplied by a factor
        sol_online[min_work_left_machine_index_slow].append(job)
    else:
        # Compare the work left of the two machines
        if work_left_fast_machines[min_work_left_machine_index_fast] < work_left_slow_machines[min_work_left_machine_index_slow - fast_nb]:
            sol_online[min_work_left_machine_index_fast].append(job)
        else:
            sol_online[min_work_left_machine_index_slow].append(job)

    return sol_online


##############################################################
#### LISEZ LE README et NE PAS MODIFIER LE CODE SUIVANT ####
##############################################################
'''if __name__=="__main__":

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

    # le bloc de lancement dégagé à l'exterieur pour ne pas le répeter pour deterministe/random
    def launching_sequence(sigma, m, fast_nb, slow_speed):
         ### global sol_online # car effacé en ingestion !!!
        sol_online  = [[] for i in range(m)]    
        for job in sigma:
            # votre algoritme est lancé ici pour une tâche job
            slow_fast_scheduling_online(sol_online, m, fast_nb, slow_speed, job)

        # Un algorithme doit attribuer toutes les tâches aux machines
        verify_solution(sigma, sol_online)
        return sol_online # retour nécessaire pour ingestion



    # Collecte des résultats
    scores = []
    
    for instance_filename in sorted(os.listdir(input_dir)):
        
        # C'est une partie pour inserer dans ingestion.py !!!!!
        # importer l'instance depuis le fichier (attention code non robuste)
        # le code repris de Safouan - refaire pour m'affanchir des numéros explicites
        instance_file = open(os.path.join(input_dir, instance_filename), "r")
        lines = instance_file.readlines()
        
        m = int(lines[1])
        fast_nb = int(lines[4])
        slow_nb = m-fast_nb
        slow_speed = int(lines[7])
        str_lu_sigma = lines[10]
        sigma = ast.literal_eval(str_lu_sigma)
        exact_solution = int(lines[13])

        # lancement conditionelle de votre algorithme
        # N.B. il est lancé par la fonction launching_sequence() 
        if mon_algo_est_deterministe():
            print("lancement d'un algo deterministe")  
            solution_online = launching_sequence(sigma, m, fast_nb, slow_speed)
            solution_eleve = val_sol(sigma, m, fast_nb, slow_speed, solution_online)  
        else:
            print("lancement d'un algo randomisé")
            runs = 10
            sample = numpy.empty(runs)
            for r in range(runs):
                solution_online = launching_sequence(sigma, m, fast_nb, slow_speed)  
                sample[r] = val_sol(sigma, m, fast_nb, slow_speed, solution_online)
            solution_eleve = numpy.mean(sample)


        best_ratio = solution_eleve/float(exact_solution)
        scores.append(best_ratio)
        # ajout au rapport
        output_file.write(instance_filename + ': score: {}\n'.format(best_ratio))

    output_file.write("Résultat moyen des ratios:" + str(sum(scores)/len(scores)))

    output_file.close()'''
if __name__=="__main__":

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

    # le bloc de lancement dégagé à l'exterieur pour ne pas le répeter pour deterministe/random
    def launching_sequence(sigma, m, fast_nb, slow_speed):
         ### global sol_online # car effacé en ingestion !!!
        sol_online  = [[] for i in range(m)]    
        for job in sigma:
            # votre algoritme est lancé ici pour une tâche job
            slow_fast_scheduling_online(sol_online, m, fast_nb, slow_speed, job)

        # Un algorithme doit attribuer toutes les tâches aux machines
        verify_solution(sigma, sol_online)
        return sol_online # retour nécessaire pour ingestion



    # Collecte des résultats
    scores = []
    
    for instance_filename in sorted(os.listdir(input_dir)):
        
        # C'est une partie pour inserer dans ingestion.py !!!!!
        # importer l'instance depuis le fichier (attention code non robuste)
        # le code repris de Safouan - refaire pour m'affanchir des numéros explicites
        instance_file = open(os.path.join(input_dir, instance_filename), "r")
        lines = instance_file.readlines()
        
        m = int(lines[1])
        fast_nb = int(lines[4])
        slow_nb = m-fast_nb
        slow_speed = int(lines[7])
        str_lu_sigma = lines[10]
        sigma = ast.literal_eval(str_lu_sigma)
        exact_solution = int(lines[13])

        # lancement conditionelle de votre algorithme
        # N.B. il est lancé par la fonction launching_sequence() 
        if mon_algo_est_deterministe():
            #print("lancement d'un algo deterministe")  
            solution_online = launching_sequence(sigma, m, fast_nb, slow_speed)
            solution_eleve = val_sol(sigma, m, fast_nb, slow_speed, solution_online)  
        else:
            #print("lancement d'un algo randomisé")
            runs = 10
            sample = numpy.empty(runs)
            for r in range(runs):
                solution_online = launching_sequence(sigma, m, fast_nb, slow_speed)  
                sample[r] = val_sol(sigma, m, fast_nb, slow_speed, solution_online)
            solution_eleve = numpy.mean(sample)


        best_ratio = solution_eleve/float(exact_solution)
        scores.append(best_ratio)
        # ajout au rapport
        print((instance_filename + ': {}'.format(best_ratio)).rjust(60))
        output_file.write(instance_filename + ': score: {}\n'.format(best_ratio))

    print(("\nRésultat moyen des ratios: " + str(sum(scores)/len(scores))).rjust(60))
    output_file.write("Résultat moyen des ratios:" + str(sum(scores)/len(scores)))

    output_file.close()
