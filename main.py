import MatrixGenerator as MG
import ShowResults as SR
import Computing as comp


def main():
    params = 1
    mg = MG.MatrixGenerator(params)
    sg = SR.ShowResults(params)
    res = comp.Computing(params)
    
    print(mg._params, sg._params, res._params)
    return 0

if __name__ == "__main__":
    main()
