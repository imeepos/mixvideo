
/**
 * 剪映
 */
export abstract class Lveditor { }
/**
 * 剪映项目
 */
export abstract class LveditorProject {
    /**
     * 项目ID
     */
    projectId: string;
    /**
     * 项目标题
     */
    projectTitle: string;
    /**
     * 项目路径
     */
    projectPath: string;
    /**
     * 草稿列表
     */
    drafts: LveditorDraft[];
}
/**
 * 剪映草稿
 */
export abstract class LveditorDraftMetaInfo { }
export abstract class LveditorDraftContent { }
export abstract class LveditorAgencyConfig { }
export abstract class LveditorDraft {
    meta_info: LveditorDraftMetaInfo;
    content: LveditorDraftContent;
    agency_config: LveditorAgencyConfig;
    name: string;
    new_version: string;
}
/**
 * 剪映素材
 */
export abstract class LveditorMaterial { }
/**
 * 剪映轨道
 */
export abstract class LveditorTrack { }
/**
 * 剪映片段
 */
export abstract class LveditorClip { }
/**
 * 剪映特效
 */
export abstract class LveditorEffect { }
/**
 * 剪映转场
 */
export abstract class LveditorTransition { }
/**
 * 剪映文字
 */
export abstract class LveditorText { }
/**
 * 剪映图片
 */
export abstract class LveditorImage { }
/**
 * 剪映视频
 */
export abstract class LveditorVideo { }
