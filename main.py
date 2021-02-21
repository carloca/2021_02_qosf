import argparse
import logging

import plotly.express as px

from src.simulations import get_circuit_to_print, run_all_combinations, run_one_combination, run_random_errors

logging.basicConfig(format='%(levelname)s:\t\t%(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger('QOSF')
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser(description='Bell state circuit with error correction simulation.')
parser.add_argument('correction', help='The type of correction to use', type=str,
                    choices=['no_correction', 'simple', 'repetition_simple', 'shor'])
parser.add_argument('--print-circuit',
                    help='Plot circuit with symbolic errors. If present all the simulation arguments '
                         'will be ignored and it will only plot the circuit.',
                    action='store_true')
parser.add_argument('--try-all', action='store_true',
                    help='Try all the possible 1-qubit error combinations. It is assumed that for 1 qubit '
                         'and its ancillas only 1 error can happen in either the qubit or one of the ancillas. '
                         'If this argument is not provided then a random error set up will be generated.')
parser.add_argument('-i', '--iterations',
                    help='The number of iterations to simulate the circuit generating a random set of errors each '
                         'time. The argument will be ignored if --try-all or --error are present. Default: 1',
                    type=int, default=1)
parser.add_argument('-p', '--probabilities', help='Probabilities, more correctly weights, for each error gate. '
                                                  'Pass as <p_i> <p_x> <p_z>.'
                                                  'If not passed, probability is equally distributed.'
                                                  'The argument will be ignored if --error is present',
                    nargs=3)
parser.add_argument('-s', '--seed', help='Seed to generate random error set.')
parser.add_argument('-e', '--error', nargs=4,
                    help='Specific error to be simulated in the format '
                         '<qubit_1> <gate_1> <qubit_2> <gate_2> where qubit_1 and qubit_2 are the qubits, '
                         'in each correction group respectively, to which apply the error and can range from 0 to '
                         'n_ancillas, while gate_1 and gate_2 are the error gates (ex: 0 x 1 z). '
                         'The argument will be ignored if --try-all is present. ',
                    type=str)
parser.add_argument('-o', '--output', help='File path to store output.', type=str)


def run_simulation():
    args = parser.parse_args()

    n_ancillas = 0
    if args.correction == 'simple':
        n_ancillas = 1
    elif args.correction == 'repetition_simple':
        n_ancillas = 2
    elif args.correction == 'shor':
        n_ancillas = 8

    if args.print_circuit:
        logger.info('Skipping simulations and printing only the circuit with symbolic errors.')
        circuit = get_circuit_to_print(n_ancillas, args.correction)
        fig = circuit.draw(output='mpl', plot_barriers=False)
        fig.show()
        return

    if args.try_all:
        logger.info('Run all possible error configuration')
        counts, err_to_counts = run_all_combinations(n_ancillas, args.correction)
    elif args.error:
        errors = [((1, int(args.error[0])), args.error[1]),
                  ((2, int(args.error[2])), args.error[3])]
        counts, error = run_one_combination(n_ancillas, args.correction, errors)
        err_to_counts = {error: counts}
        logger.info(f'Run with error {error}')
    else:

        logger.info(f'Run {args.iterations} times with random errors with '
                    f'{args.probabilities if args.probabilities else "equal"} probabilities')
        counts, err_to_counts = run_random_errors(n_ancillas,
                                                  args.correction,
                                                  args.iterations,
                                                  [float(p) for p in args.probabilities] if args.probabilities
                                                  else None,
                                                  args.seed)

    logger.info('Plot the counts')
    fig = px.bar(x=counts.keys(), y=counts.values(), labels={'x': 'Measured state', 'y': 'Counts'})
    fig.show()

    if args.output:
        logger.info(f'Writing output in {args.output}')
        with open(args.output, 'w') as f:
            f.write(f'Total counts: {dict(counts)}\n\n')
            f.write(f'Details with error split:\n')
            for key, value in err_to_counts.items():
                f.write(f'{key}\t{value}\n')


if __name__ == "__main__":
    run_simulation()
