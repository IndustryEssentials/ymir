
declare namespace YModels {


    export type BackendData = {
        [key: string]: any,
    }

    export interface Group {
        id: number,
        name: string,
        projectId: number,
        createTime: string,
    }

    export interface Result {
        id: number,
        groupId: number,
        projectId: number,
        name: string,
        versionName: string,
        version: number,
        keywords: Array<string>,
        isProtected?: Boolean,
        state: number,
        createTime: string,
        updateTime: string,
        hash: string,
        taskId: number,
        progress: number,
        taskState: number,
        taskType: number,
        duration: number,
        durationLabel?: string,
        taskName: string,
        project?: Project,
        task?: Task,
        hidden: boolean,
        description: string,
    }

    type Keywords = {
        [key: string]: number,
    }
    type CK = {
        [key: string]: any,
    }
    type AnnotationsCount = {
        count: Keywords,
        keywords: Array<string>,
        negative: number,
        total: number,
    }
    type AnylysisAnnotation = {
        keywords: Keywords,
        total: number,
        average: number,
        negative: number,
        quality: Array<BackendData>,
        area: Array<BackendData>,
        areaRatio: Array<BackendData>,
    }
    export interface DatasetGroup extends Group {
        versions?: Array<Dataset>,
    }

    export interface Dataset extends Result {
        keywordCount: number,
        isProtected: Boolean,
        assetCount: number,
        gt?: AnnotationsCount,
        pred?: AnnotationsCount,
        inferClass?: Array<string>,
        cks?: BackendData,
        tags?: BackendData,
    }

    export interface InferDataset extends Dataset {
        inferModelId: number[],
        inferModel?: Model,
        inferDatasetId: number,
        inferDataset?: Dataset,
        inferConfig: ImageConfig,
    }

    export interface DatasetAnalysis {
        name: string,
        version: number,
        versionName: string,
        assetCount: number,
        totalAssetMbytes: number,
        assetBytes: Array<BackendData>,
        assetHWRatio: Array<BackendData>,
        assetArea: Array<BackendData>,
        assetQuality: Array<BackendData>,
        gt: AnylysisAnnotation,
        pred: AnylysisAnnotation,
        inferClass?: Array<string>,
        cks?: BackendData,
        tags?: BackendData,
    }

    export interface Asset {
        id: number,
        hash: string,
        keywords: Array<string>,
        url: string,
        metadata?: {
            width: number,
            height: number,
            channel: number,
        },
        size?: number,
        annotations: Array<Annotation>,
        evaluated?: boolean,
        cks?: CK,
    }

    export interface Annotation {
        keyword: string,
        box: {
            x: number,
            y: number,
            w: number,
            h: number,
            rotate_angle: number,
        }
        color?: string,
        score?: number,
        gt?: boolean,
        cm: number,
        tags?: CK,
    }


    export interface Stage {
        id: number,
        name: string,
        map: number,
        modelId?: number,
        modelName?: string,
    }
    export interface ModelGroup extends Group { }
    export interface Model extends Result {
        map: number,
        url: string,
        stages?: Array<Stage>,
        recommendStage: number,
    }
    export interface Project {
        id: number,
        name: string,
        type: number,
        keywords: Array<string>,
        candidateTrainSet: number,
        trainSet?: DatasetGroup,
        testSet?: Dataset,
        miningSet?: Dataset,
        testingSets?: Array<number>,
        setCount: number,
        trainSetVersion?: number,
        model?: number,
        modelStage?: Array<number>,
        modelCount: number,
        miningStrategy: number,
        chunkSize?: number,
        currentIteration?: Iteration,
        round: number,
        currentStage: number,
        createTime: string,
        updateTime: string,
        description?: string,
        isExample?: boolean,
        hiddenDatasets: Array<number>,
        hiddenModels: Array<number>,
        enableIteration: boolean,
        totalAssetCount: number,
        runningTaskCount: number,
        totalTaskCount: number,
    }

    export type ImageConfig = { [key: string]: number | string, }
    export type DockerImageConfig = {
        type: number,
        config: ImageConfig,
    }
    export interface Image {
        id: number,
        name: string,
        state: number,
        isShared: boolean,
        functions: Array<number>,
        configs: Array<DockerImageConfig>,
        url: string,
        liveCode?: boolean,
        description: string,
        createTime: string,
        related?: Array<Image>,
    }

    type DatasetId = number

    export interface Iteration {
        id: number,
        projectId: number,
        name?: string,
        round: number,
        currentStep: Step,
        steps: Step[],
        currentStage: number,
        testSet?: DatasetId,
        trainSet?: DatasetId,
        trainUpdateSet: DatasetId,
        wholeMiningSet: DatasetId,
        miningSet?: DatasetId,
        miningResult?: DatasetId,
        labelSet?: DatasetId,
        model?: number,
        prevIteration: number,
    }

    export interface Step {
        id: number,
        finished: boolean,
        name: string,
        percent: number,
        presetting: any,
        state: number,
        taskId: number,
        taskType: number,
    }

    interface ShareImage {
        docker_name: string,
        functions?: string,
        contributor?: string,
        organization?: string,
        description?: string,
    }

    type PlainObject = {
        [key: string]: any,
    }

    export interface Task {
        name: string,
        type: number,
        project_id: number,
        is_deleted: number,
        create_datetime: string,
        update_datetime: string,
        id: number,
        hash: string,
        state: number,
        error_code: number,
        duration: number,
        percent: number,
        parameters: Parameters,
        config: PlainObject,
        result_type: number,
        is_terminated: boolean,
    }

    type MergeStrategy = 0 | 1 | 2
    type Preprocess = {
        [func: string]: PlainObject,
    }

    interface Parameters {
        dataset_id?: number,
        keywords?: string[],
        extra_url?: string,
        labellers?: string[],
        annotation_type?: number,
        validation_dataset_id?: number,
        network?: string,
        backbone?: string,
        hyperparameter?: string,
        strategy?: MergeStrategy,
        preprocess?: Preprocess,
        model_id?: number,
        model_stage_id?: number,
        mining_algorithm?: string,
        top_k?: number,
        generate_annotations?: boolean,
        docker_image?: string,
        docker_image_id?: number,
    }

}
