"""
Zemberek: Turkish Tokenization Example
Java Code Example: https://bit.ly/2PsLOkj
"""
from typing import List
from jpype import JClass, JString, getDefaultJVMPath, shutdownJVM, startJVM, java

ZEMBEREK_PATH = r'C:\brandzone\data_science1\zemberek-full.jar' 
startJVM(getDefaultJVMPath(), '-ea', '-Djava.class.path=%s' % (ZEMBEREK_PATH))

__all__: List[str] = ['run']

TurkishMorphology: JClass = JClass('zemberek.morphology.TurkishMorphology')
WordAnalysis: JClass = JClass('zemberek.morphology.analysis.WordAnalysis')


def run(word: str) -> None:
    """
    Stemming and lemmatization example.
    Args:
        word (str): Word to apply stemming and lemmatization.
    """

    morphology: TurkishMorphology = TurkishMorphology.createWithDefaults()

    print('\nResults:')

    results: WordAnalysis = morphology.analyzeAndDisambiguate(word).bestAnalysis()
    print(results)
    for result in results:
        print(
            f'{str(result.formatLong())}'
            f'\n\tStems ='
            f' {", ".join([str(result) for result in result.getStems()])}'
            f'\n\tLemmas ='
            f' {", ".join([str(result) for result in result.getLemmas()])}'
        )

run("playing")

shutdownJVM()