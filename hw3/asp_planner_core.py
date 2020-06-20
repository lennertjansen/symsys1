from planning import PlanningProblem, Action, Expr, expr
import planning

import clingo

#TODO: remove before submission
import pdb

def solve_planning_problem_using_ASP(planning_problem,t_max):
    """
    If there is a plan of length at most t_max that achieves the goals of a given planning problem,
    starting from the initial state in the planning problem, returns such a plan of minimal length.
    If no such plan exists of length at most t_max, returns None.

    Finding a shortest plan is done by encoding the problem into ASP, calling clingo to find an
    optimized answer set of the constructed logic program, and extracting a shortest plan from this
    optimized answer set.

    NOTE: still needs to be implemented. Currently returns None for every input.

    Parameters:
        planning_problem (PlanningProblem): Planning problem for which a shortest plan is to be found.
        t_max (int): The upper bound on the length of plans to consider.

    Returns:
        (list(Expr)): A list of expressions (each of which specifies a ground action) that composes
        a shortest plan for planning_problem (if some plan of length at most t_max exists),
        and None otherwise.
    """

    # This code must consist of the following phases
    # 1) Read and parse the planning_problem and t_max such that all the necessary information can be easily accessed and used
    # 2) Encode the planning problem (and plan length constrain t_max) into an ASP P.
    # 3) Use clingo to find the answer sets of P and then optimize for the ideal AS.
    # 4) Have clingo return the predicates that correspond to the relevant moves, actions and objects for reaching the goal
    # 5) Decode this information back into the language of the planning_problem
    # 6) Return the plan
    # 7) ????
    # 8) Profit

    ## Phase 1) Read and parse the planning problem
    # store lists of planning problem's initial states, goals, and actions
    initial_states = planning_problem.initial
    goals = planning_problem.goals
    actions = planning_problem.actions

    # TODO: remove before submission
    # Overview of planning problem
    print("#"*81)
    print("HIER")
    print("Initial state: ", initial_states)
    print("Goal state: ", goals)
    print("Actions: ", actions)
    for action in actions:
        print("Action: ", action)
        print("Preconditions: ", action.precond)
        print("Effect: ", action.effect)

    # to be filled with all states
    states = []
    # parse the initial states
    #NB: roughly same parsing structure applies to goals and states, so comments
    # will become less frequent moving forward in this phase
    for initial_state in initial_states:
        # if not negated expresion, just add state
        if initial_state.op != '~':
            if initial_state not in states:
                states.append(initial_state)
        # if negated expression, add args of state
        else:
            print("#"*20)
            print("Negated expression comin thru")
            print("#"*20)
            for argument in initial_state.args:
                if argument not in states:
                    states.append(argument)

    print("States: ", states)

    # parse goal states
    for goal in goals:
        if goal.op != "~":
            if goal not in states:
                states.append(goal)
        else:
            for argument in goal.args:
                if argument not in states:
                    states.append(argument)

    print("States: ", states)

    # parse actions
    for action in actions:
        # add precondition states
        for precond_sate in action.precond:
            if precond_sate.op != "~":
                if precond_sate not in states:
                    states.append(precond_sate)
            else:
                for argument in precond_state.args:
                    if argument not in states:
                        states.append(argument)
        # add effects of actions
        for effect in action.effect:
            if effect.op != "~":
                if effect not in states:
                    states.append(effect)
            else:
                for argument in effect.args:
                    if argument not in states:
                        states.append(argument)
    print("States: ", states)

    ## Phase 2) Encode the parse planning problem into an ASP
    # empty string to be filled with answer set program
    asp_code = """"""

    # add t_max as constant and declare the time steps using facts
    asp_code += f"%Constants and declaration of time steps and state variables. \n"
    asp_code += f"#const t_max={t_max}. \n"
    asp_code += f"time(1..t_max). \n"
    #TODO: figure out if this needs to be here
    #TODO: CHANGE THESE NAMES
    asp_code += f"#const s={len(states)}. \n"
    asp_code += f"state_variables(1..s). \n"

    # Add empty lines for readability of  ASP
    asp_code += "\n"
    asp_code += "\n"

    # declare the initial states using facts and index them at time T = 0
    # state(TIME, STATE_INDEX, TRUE/FALSE)
    asp_code += f"%Declare initial states. \n"
    for idx, state in enumerate(states):
        if state in initial_states:
            # if state in initial states, set state predicate to true
            asp_code += f"state(0, {idx}, 1). \n"
        else:
            asp_code += f"state(0, {idx}, 0). \n"


    # Add empty lines for readability of  ASP
    asp_code += "\n"
    asp_code += "\n"

    # Set (pre)condition restrictions for actions
    asp_code += f"%Declare possible actions and corresponding preconditions. \n"
    for idx, action in enumerate(actions):
        action_string = f"{{action(T, {idx})}} :- time(T)" #TODO: Why double brackets?
        for precond_state in action.precond:
            action_string += f", state(T - 1, {states.index(precond_state)}, 1)"
        action_string += ". \n"
        asp_code += action_string

    # Add empty lines for readability of  ASP
    asp_code += "\n"
    asp_code += "\n"

    asp_code += f"%Effects of actions hold true if action occurs. \n"
    for action_idx, action in enumerate(actions):
        effect_asp_code = ""

        for effect_idx, effect in enumerate(action.effect):

            if effect_idx > 0:
                effect_asp_code += ", "

            if effect.op != "~":
                effect_asp_code += f"state(T, {states.index(effect)}, 1)"
            else:
                for argument in effect.args:
                    effect_asp_code += f"state(T, {states.index(argument)}, 0)"

        effect_asp_code += f" :- action(T, {action_idx}), time(T). \n"
        asp_code += effect_asp_code

    # Add empty lines for readability of  ASP
    asp_code += "\n"
    asp_code += "\n"


    # No parallel actions allowed
    for idx1, action_1 in enumerate(actions):
        for idx2, action_2 in enumerate(actions):
            if idx1 < idx2:
                asp_code += f":- action(T, {idx1}), action(T, {idx2}), time(T). \n"

    # Add empty lines for readability of  ASP
    asp_code += "\n"
    asp_code += "\n"

    # If no changes occur, carry truth over to next timestep
    for idx, state in enumerate(states):
        asp_code += f"state(T, {idx}, 1) :- state(T - 1, {idx}, 1), not state(T, {idx}, 0), time(T). \n"
        asp_code += f"state(T, {idx}, 0) :- state(T - 1, {idx}, 0), not state(T, {idx}, 1), time(T). \n"

    # Add empty lines for readability of  ASP
    asp_code += "\n"
    asp_code += "\n"

    # Enforce goal states
    for goal in goals:
        asp_code += f":- not state(t_max, {states.index(goal)}, 1). \n"

    # Add empty lines for readability of  ASP
    asp_code += "\n"
    asp_code += "\n"

    # optimize for minimal time steps
    min_asp_code = "#minimize{\n"

    for idx, action in enumerate(actions):
        min_asp_code += f"T, state_variables({idx + 1}) : action(T, {idx}), time(T)"
        if idx < len(actions) - 1:
            min_asp_code += ";\n"
    min_asp_code += "\n}.\n"
    asp_code += min_asp_code

    # Add empty lines for readability of  ASP
    asp_code += "\n"
    asp_code += "\n"

    asp_code += "#show action/2."



    print("#"*81)
    print("ASP COMIN THRUUU")
    print("#"*81)
    print(asp_code)

    # ## Phase 4) optimize using clingo
    # print_answer_sets(asp_code)
    # # pdb.set_trace()
    #
    # #### TESTING: Lets see what this here function really do be like
    #
    # plan1 = [expr('LeftSock'), expr('RightSock'), expr('LeftShoe'), expr('RightShoe')]
    # plan2 = [expr('LeftSock'), expr('LeftShoe'), expr('RightSock'), expr('RightShoe')]
    # plan3 = [expr('RightSock'), expr('RightShoe'), expr('LeftSock'), expr('LeftShoe')]
    # plan4 = [expr('RightSock'), expr('LeftSock'), expr('LeftShoe'), expr('RightShoe')]
    #
    # ## Phase 5) Decode back into planning problem language and return solution

    plan = asp_to_plan(asp_code, actions)

    return plan

# Original function Taken from KRR-course GitHub repo example: https://github.com/rdehaan/KRR-course/blob/master/examples/guide-to-asp.ipynb
# Adapted such that it returns the answer sets, with optional print
def print_answer_sets(program):
    """
    Gives us the answer sets of a given answer set program, and display the atoms in the answer set sorted alphabetically.
    Code taken from: https://github.com/rdehaan/KRR-course/blob/master/examples/guide-to-asp.ipynb
    """
    # Load the answer set program, and call the grounder
    control = clingo.Control();
    control.add("base", [], program);
    control.ground([("base", [])]);
    # Define a function that will be called when an answer set is found
    # This function sorts the answer set alphabetically, and prints it
    def on_model(model):
        sorted_model = [str(atom) for atom in model.symbols(shown=True)];
        sorted_model.sort();
        print("Answer set: {{{}}}".format(", ".join(sorted_model)));
    # Ask clingo to find all models (using an upper bound of 0 gives all models)
    control.configuration.solve.models = 1;
    # Call the clingo solver, passing on the function on_model for when an answer set is found
    answer = control.solve(on_model=on_model)
    # Print a message when no answer set was found
    if answer.satisfiable == False:
        print("No answer sets");

# Define a function that will be called when an answer set is found
# This function sorts the answer set alphabetically, and prints it
def on_model(model, print = False):
    sorted_model = [str(atom) for atom in model.symbols(shown=True)];
    sorted_model.sort();
    print("Answer set: {{{}}}".format(", ".join(sorted_model)));

def asp_to_plan(program, actions_list, print_as = False):
    """
    Takes answer set program and list of possible actions in planning problem,
    solves program and returns plan as list of action expressions.
    Based on print_answer_sets(), from: https://github.com/rdehaan/KRR-course/blob/master/examples/guide-to-asp.ipynb
    """

    # Load the answer set program, and call the grounder
    control = clingo.Control();
    control.add("base", [], program); # asp_code = program
    control.ground([("base", [])]);

    # Define a function that will be called when an answer set is found
    # This function sorts the answer set alphabetically, and prints it
    sorted_models = []
    def on_model(model):
        sorted_model = [str(atom) for atom in model.symbols(shown=True)];
        sorted_model.sort();
        sorted_models.append(sorted_model)
        if print_as: print("Answer Sset: {{{}}}".format(", ".join(sorted_model)))
    # Ask clingo to find all models (using an upper bound of 0 gives all models)
    control.configuration.solve.models = 0;
    # Call the clingo solver, passing on the function on_model for when an answer set is found
    answer = control.solve(on_model=on_model)

    # Print a message when no answer set was found
    if answer.satisfiable == False:
        print("No answer sets");

    # empty list to be filled with actions expressions
    plan = []

    # iterate over action predicates from (the first of the optimal) model(s),
    # find action index, and append relevant action to plan
    #TODO: this now arbitrarily takes the first of the optimal models, does this
    # have any consequences?
    for asp_action_string in sorted_models[0]:
        action_plan_idx = int(asp_action_string[-2])
        action_plan_string = str(actions_list[action_plan_idx])
        plan.append(expr(action_plan_string))

    return plan
