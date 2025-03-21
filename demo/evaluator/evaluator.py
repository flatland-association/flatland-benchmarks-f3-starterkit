from flatland.evaluators.service import FlatlandRemoteEvaluationService

if __name__ == '__main__':
    print("/ start grader", flush=True)
    grader = FlatlandRemoteEvaluationService(
        test_env_folder="/tmp/debug-environments",
        visualize=False,
        verbose=False,
    )
    grader.run()
    print("\\ end grader", flush=True)
