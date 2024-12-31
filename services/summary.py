from dependencies.model_factory import summary_model

def make_summary(text):
    return summary_model.exec(text)
