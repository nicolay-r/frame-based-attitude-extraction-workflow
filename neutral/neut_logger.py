class NeutralOpinionExtractionLogger:
    def __init__(self):
        self.new_opinions = 0
        self.new_opinions = 0
        self.existed_opinions = 0
        self.sentences = 0
        self.documents = 0

    @property
    def NewOpinions(self):
        return self.new_opinions

    @property
    def ExistedOpinions(self):
        return self.existed_opinions

    @property
    def Sentences(self):
        return self.sentences

    @property
    def Documents(self):
        return self.documents

    def reg_doc(self):
        self.documents += 1

    def reg_existed_opin(self):
        self.existed_opinions += 1

    def reg_new_opin(self, count):
        self.new_opinions += count

    def reg_sent(self):
        self.sentences += 1

    def iter_data(self):
        yield "Docs: {}\n".format(self.Documents)
        yield "Sentences: {}\n".format(self.Sentences)
        yield "Opinions existed: {}\n".format(self.ExistedOpinions)
        yield "Neutral opins added: {}\n".format(self.NewOpinions)
        yield "Neutral opins added per doc (avg.): {}\n".format(round(float(self.NewOpinions) / self.Documents, 2))
        yield "Neutral opins added per sentence (avg.): {}\n".format(round(float(self.NewOpinions) / self.Sentences, 2))
        yield "Percent of added: {}%\n".format(round(100 * float(self.NewOpinions) / self.ExistedOpinions, 2))
