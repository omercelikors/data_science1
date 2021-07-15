"""
Zemberek: Turkish Tokenization Example
Java Code Example: https://bit.ly/2PsLOkj
"""
from typing import List
from jpype import JClass, JString, getDefaultJVMPath, shutdownJVM, startJVM, java

ZEMBEREK_PATH = r'C:\brandzone\data_science1\zemberek-full.jar' 
startJVM(getDefaultJVMPath(), '-ea', '-Djava.class.path=%s' % (ZEMBEREK_PATH))

TurkishMorphology: JClass = JClass('zemberek.morphology.TurkishMorphology')
TurkishSentenceNormalizer: JClass = JClass(
    'zemberek.normalization.TurkishSentenceNormalizer'
)
Paths: JClass = JClass('java.nio.file.Paths')


def run(text: str) -> None:
    """
    Noisy text normalization example.
    Args:
        text (str): Noisy text to normalize.
    """

    normalizer = TurkishSentenceNormalizer(
        TurkishMorphology.createWithDefaults(),
        Paths.get("C:/brandzone/data_science1/zemberek_data/normalization"),
		Paths.get("C:/brandzone/data_science1/zemberek_data/lm/lm.2gram.slm"),
    )

    print(f'\nNormalized: {normalizer.normalize(JString(text))}')

run("bars")

shutdownJVM()