
from mir.protos import mir_command_pb2 as mirpb


def evaluate(prediction: mirpb.SingleTaskAnnotations, ground_truth: mirpb.SingleTaskAnnotations,
             config: mirpb.EvaluateConfig, assets_metadata: mirpb.MirMetadatas) -> mirpb.Evaluation:
    pass
