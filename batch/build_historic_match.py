from tennis_win_fun.build_historic.historic_launcher import BuildHistoric

bh = BuildHistoric()


def main():
    """
    Main function to build historic data.
    """
    bh.run_match_historic()


if __name__ == "__main__":
    main()
