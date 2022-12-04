import depthai as dai

class RGBPipeline:
    'Base class for DepthAI RGB camera pipeline'

    def __init__(self, streamName="video") -> None:
        self.streamName = streamName
        # Create pipeline
        self.pipeline = dai.Pipeline()

        # Define source and output
        camRgb = self.pipeline.create(dai.node.ColorCamera)
        xoutVideo = self.pipeline.create(dai.node.XLinkOut)
        xoutVideo.setStreamName(streamName)
        
        # Properties
        camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
        camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        camRgb.setVideoSize(1920, 1080)

        xoutVideo.input.setBlocking(False)
        xoutVideo.input.setQueueSize(1)

        # Linking
        camRgb.video.link(xoutVideo.input)

    def getPipeline(self):
        return self.pipeline

    def getStreamName(self):
        return self.streamName