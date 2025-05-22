from flatland.evaluators.service import FlatlandRemoteEvaluationService

if __name__ == '__main__':
    print("/ start grader", flush=True)
    grader = FlatlandRemoteEvaluationService(
        test_env_folder="/tmp/debug-environments",
        visualize=False,
        verbose=False,
        # temporarily use pickle because of fastenum failing with msgpack: https://github.com/flatland-association/flatland-rl/pull/214/files
        use_pickle=True
    )
    grader.run()
    print("\\ end grader", flush=True)
