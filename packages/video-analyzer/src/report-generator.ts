/**
 * Report generation for video analysis results
 */

import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import {
  AnalysisReport,
  VideoAnalysisResult,
  FolderMatchResult,
  VideoAnalyzerError
} from './types';

const writeFile = promisify(fs.writeFile);
const mkdir = promisify(fs.mkdir);

/**
 * Report generation options
 */
export interface ReportOptions {
  /** Output format */
  format: 'xml' | 'json' | 'csv' | 'html';
  /** Output file path */
  outputPath: string;
  /** Include thumbnails in report */
  includeThumbnails?: boolean;
  /** Include detailed analysis data */
  includeDetailedAnalysis?: boolean;
  /** Include folder matching results */
  includeFolderMatching?: boolean;
  /** Custom report title */
  title?: string;
  /** Additional metadata */
  metadata?: Record<string, any>;
}

/**
 * Report generator class
 */
export class ReportGenerator {
  /**
   * Generate comprehensive analysis report
   */
  async generateReport(
    videoResults: VideoAnalysisResult[],
    folderMatches: Record<string, FolderMatchResult[]> = {},
    options: ReportOptions
  ): Promise<string> {
    try {
      // Ensure output directory exists
      await this.ensureOutputDirectory(options.outputPath);

      // Build report data
      const report = this.buildReport(videoResults, folderMatches, options);

      // Generate report based on format
      let reportContent: string;
      switch (options.format) {
        case 'xml':
          reportContent = this.generateXMLReport(report);
          break;
        case 'json':
          reportContent = this.generateJSONReport(report);
          break;
        case 'csv':
          reportContent = this.generateCSVReport(report);
          break;
        case 'html':
          reportContent = this.generateHTMLReport(report);
          break;
        default:
          throw new Error(`Unsupported format: ${options.format}`);
      }

      // Write report to file
      await writeFile(options.outputPath, reportContent, 'utf-8');

      return options.outputPath;

    } catch (error) {
      throw new VideoAnalyzerError(
        `Report generation failed: ${this.getErrorMessage(error)}`,
        'REPORT_GENERATION_FAILED',
        error
      );
    }
  }

  private getErrorMessage(error: unknown){
    return error instanceof Error ? error.message : String(error);
  }

  /**
   * Build report data structure
   */
  private buildReport(
    videoResults: VideoAnalysisResult[],
    folderMatches: Record<string, FolderMatchResult[]>,
    options: ReportOptions
  ): AnalysisReport {
    const totalProcessingTime = videoResults.reduce(
      (sum, result) => sum + result.processingTime,
      0
    );

    const totalScenes = videoResults.reduce(
      (sum, result) => sum + result.scenes.length,
      0
    );

    const totalObjects = videoResults.reduce(
      (sum, result) => sum + result.objects.length,
      0
    );

    // Extract common themes
    const allKeywords = videoResults.flatMap(result => result.summary.keywords);
    const keywordCounts = this.countOccurrences(allKeywords);
    const commonThemes = Object.entries(keywordCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10)
      .map(([keyword]) => keyword);

    // Extract recommended categories
    const allTopics = videoResults.flatMap(result => result.summary.topics);
    const topicCounts = this.countOccurrences(allTopics);
    const recommendedCategories = Object.entries(topicCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([topic]) => topic);

    return {
      metadata: {
        generatedAt: new Date(),
        version: '1.0.0',
        totalVideos: videoResults.length,
        totalProcessingTime
      },
      videoResults,
      folderMatches: options.includeFolderMatching ? folderMatches : undefined,
      summary: {
        totalScenes,
        totalObjects,
        commonThemes,
        recommendedCategories
      },
      exportOptions: {
        format: options.format,
        includeImages: false,
        includeThumbnails: options.includeThumbnails || false
      }
    };
  }

  /**
   * Generate XML report
   */
  private generateXMLReport(report: AnalysisReport): string {
    const xml = ['<?xml version="1.0" encoding="UTF-8"?>'];
    xml.push('<VideoAnalysisReport>');
    
    // Metadata
    xml.push('  <Metadata>');
    xml.push(`    <GeneratedAt>${report.metadata.generatedAt.toISOString()}</GeneratedAt>`);
    xml.push(`    <Version>${report.metadata.version}</Version>`);
    xml.push(`    <TotalVideos>${report.metadata.totalVideos}</TotalVideos>`);
    xml.push(`    <TotalProcessingTime>${report.metadata.totalProcessingTime}</TotalProcessingTime>`);
    xml.push('  </Metadata>');

    // Summary
    xml.push('  <Summary>');
    xml.push(`    <TotalScenes>${report.summary.totalScenes}</TotalScenes>`);
    xml.push(`    <TotalObjects>${report.summary.totalObjects}</TotalObjects>`);
    xml.push('    <CommonThemes>');
    report.summary.commonThemes.forEach(theme => {
      xml.push(`      <Theme>${this.escapeXML(theme)}</Theme>`);
    });
    xml.push('    </CommonThemes>');
    xml.push('    <RecommendedCategories>');
    report.summary.recommendedCategories.forEach(category => {
      xml.push(`      <Category>${this.escapeXML(category)}</Category>`);
    });
    xml.push('    </RecommendedCategories>');
    xml.push('  </Summary>');

    // Video Results
    xml.push('  <VideoResults>');
    report.videoResults.forEach((result, index) => {
      xml.push(`    <Video id="${index + 1}">`);
      xml.push(`      <FileName>${this.escapeXML(result.metadata.file.name)}</FileName>`);
      xml.push(`      <FilePath>${this.escapeXML(result.metadata.file.path)}</FilePath>`);
      xml.push(`      <FileSize>${result.metadata.file.size}</FileSize>`);
      xml.push(`      <AnalyzedAt>${result.analyzedAt.toISOString()}</AnalyzedAt>`);
      xml.push(`      <ProcessingTime>${result.processingTime}</ProcessingTime>`);
      
      // Summary
      xml.push('      <Summary>');
      xml.push(`        <Description>${this.escapeXML(result.summary.description)}</Description>`);
      xml.push('        <Keywords>');
      result.summary.keywords.forEach(keyword => {
        xml.push(`          <Keyword>${this.escapeXML(keyword)}</Keyword>`);
      });
      xml.push('        </Keywords>');
      xml.push('        <Topics>');
      result.summary.topics.forEach(topic => {
        xml.push(`          <Topic>${this.escapeXML(topic)}</Topic>`);
      });
      xml.push('        </Topics>');
      xml.push('      </Summary>');

      // Scenes
      xml.push('      <Scenes>');
      result.scenes.forEach((scene, sceneIndex) => {
        xml.push(`        <Scene id="${sceneIndex + 1}">`);
        xml.push(`          <StartTime>${scene.startTime}</StartTime>`);
        xml.push(`          <EndTime>${scene.endTime}</EndTime>`);
        xml.push(`          <Duration>${scene.duration}</Duration>`);
        xml.push(`          <Description>${this.escapeXML(scene.description)}</Description>`);
        xml.push(`          <Confidence>${scene.confidence}</Confidence>`);
        xml.push('        </Scene>');
      });
      xml.push('      </Scenes>');

      // Objects
      xml.push('      <Objects>');
      result.objects.forEach((object, objectIndex) => {
        xml.push(`        <Object id="${objectIndex + 1}">`);
        xml.push(`          <Name>${this.escapeXML(object.name)}</Name>`);
        xml.push(`          <Category>${this.escapeXML(object.category)}</Category>`);
        xml.push(`          <Confidence>${object.confidence}</Confidence>`);
        xml.push('        </Object>');
      });
      xml.push('      </Objects>');

      // Product Features (if available)
      if (result.productFeatures) {
        xml.push('      <ProductFeatures>');
        xml.push('        <Appearance>');
        xml.push('          <Colors>');
        result.productFeatures.appearance.colors.forEach(color => {
          xml.push(`            <Color>${this.escapeXML(color)}</Color>`);
        });
        xml.push('          </Colors>');
        xml.push(`          <Shape>${this.escapeXML(result.productFeatures.appearance.shape)}</Shape>`);
        xml.push(`          <Size>${this.escapeXML(result.productFeatures.appearance.size)}</Size>`);
        xml.push(`          <Style>${this.escapeXML(result.productFeatures.appearance.style)}</Style>`);
        xml.push('        </Appearance>');
        xml.push('        <Materials>');
        result.productFeatures.materials.forEach(material => {
          xml.push(`          <Material>${this.escapeXML(material)}</Material>`);
        });
        xml.push('        </Materials>');
        xml.push('        <Functionality>');
        result.productFeatures.functionality.forEach(func => {
          xml.push(`          <Function>${this.escapeXML(func)}</Function>`);
        });
        xml.push('        </Functionality>');
        xml.push('      </ProductFeatures>');
      }

      xml.push('    </Video>');
    });
    xml.push('  </VideoResults>');

    // Folder Matches (if included)
    if (report.folderMatches) {
      xml.push('  <FolderMatches>');
      Object.entries(report.folderMatches).forEach(([videoPath, matches]) => {
        xml.push(`    <VideoMatches videoPath="${this.escapeXML(videoPath)}">`);
        matches.forEach((match, matchIndex) => {
          xml.push(`      <Match id="${matchIndex + 1}">`);
          xml.push(`        <FolderPath>${this.escapeXML(match.folderPath)}</FolderPath>`);
          xml.push(`        <FolderName>${this.escapeXML(match.folderName)}</FolderName>`);
          xml.push(`        <Confidence>${match.confidence}</Confidence>`);
          xml.push(`        <Action>${match.action}</Action>`);
          xml.push('        <Reasons>');
          match.reasons.forEach(reason => {
            xml.push(`          <Reason>${this.escapeXML(reason)}</Reason>`);
          });
          xml.push('        </Reasons>');
          xml.push('      </Match>');
        });
        xml.push('    </VideoMatches>');
      });
      xml.push('  </FolderMatches>');
    }

    xml.push('</VideoAnalysisReport>');
    return xml.join('\n');
  }

  /**
   * Generate JSON report
   */
  private generateJSONReport(report: AnalysisReport): string {
    return JSON.stringify(report, null, 2);
  }

  /**
   * Generate CSV report
   */
  private generateCSVReport(report: AnalysisReport): string {
    const headers = [
      'FileName',
      'FilePath',
      'FileSize',
      'ProcessingTime',
      'ScenesCount',
      'ObjectsCount',
      'Keywords',
      'Topics',
      'Description'
    ];

    const rows = [headers.join(',')];

    report.videoResults.forEach(result => {
      const row = [
        this.escapeCSV(result.metadata.file.name),
        this.escapeCSV(result.metadata.file.path),
        result.metadata.file.size.toString(),
        result.processingTime.toString(),
        result.scenes.length.toString(),
        result.objects.length.toString(),
        this.escapeCSV(result.summary.keywords.join('; ')),
        this.escapeCSV(result.summary.topics.join('; ')),
        this.escapeCSV(result.summary.description)
      ];
      rows.push(row.join(','));
    });

    return rows.join('\n');
  }

  /**
   * Generate HTML report
   */
  private generateHTMLReport(report: AnalysisReport): string {
    const html = ['<!DOCTYPE html>'];
    html.push('<html lang="zh-CN">');
    html.push('<head>');
    html.push('  <meta charset="UTF-8">');
    html.push('  <meta name="viewport" content="width=device-width, initial-scale=1.0">');
    html.push('  <title>视频分析报告</title>');
    html.push('  <style>');
    html.push('    body { font-family: Arial, sans-serif; margin: 20px; }');
    html.push('    .header { background: #f5f5f5; padding: 20px; border-radius: 5px; }');
    html.push('    .summary { margin: 20px 0; }');
    html.push('    .video-result { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }');
    html.push('    .scenes, .objects { margin: 10px 0; }');
    html.push('    .scene, .object { background: #f9f9f9; padding: 5px; margin: 5px 0; border-radius: 3px; }');
    html.push('  </style>');
    html.push('</head>');
    html.push('<body>');
    
    // Header
    html.push('  <div class="header">');
    html.push('    <h1>视频分析报告</h1>');
    html.push(`    <p>生成时间：${report.metadata.generatedAt.toLocaleString('zh-CN')}</p>`);
    html.push(`    <p>总视频数：${report.metadata.totalVideos}</p>`);
    html.push(`    <p>总处理时间：${report.metadata.totalProcessingTime}ms</p>`);
    html.push('  </div>');

    // Summary
    html.push('  <div class="summary">');
    html.push('    <h2>分析摘要</h2>');
    html.push(`    <p>总场景数：${report.summary.totalScenes}</p>`);
    html.push(`    <p>总物体数：${report.summary.totalObjects}</p>`);
    html.push(`    <p>常见主题：${report.summary.commonThemes.join('、')}</p>`);
    html.push('  </div>');

    // Video Results
    html.push('  <div class="video-results">');
    html.push('    <h2>视频分析结果</h2>');
    report.videoResults.forEach((result, index) => {
      html.push(`    <div class="video-result">`);
      html.push(`      <h3>${index + 1}. ${this.escapeHTML(result.metadata.file.name)}</h3>`);
      html.push(`      <p><strong>文件路径：</strong>${this.escapeHTML(result.metadata.file.path)}</p>`);
      html.push(`      <p><strong>文件大小：</strong>${result.metadata.file.size} bytes</p>`);
      html.push(`      <p><strong>处理时间：</strong>${result.processingTime}ms</p>`);
      html.push(`      <p><strong>描述：</strong>${this.escapeHTML(result.summary.description)}</p>`);
      
      if (result.scenes.length > 0) {
        html.push('      <div class="scenes">');
        html.push('        <h4>场景分析</h4>');
        result.scenes.forEach(scene => {
          html.push(`        <div class="scene">`);
          html.push(`          <strong>${scene.startTime}s - ${scene.endTime}s:</strong> ${this.escapeHTML(scene.description)}`);
          html.push('        </div>');
        });
        html.push('      </div>');
      }

      if (result.objects.length > 0) {
        html.push('      <div class="objects">');
        html.push('        <h4>物体识别</h4>');
        result.objects.forEach(object => {
          html.push(`        <div class="object">`);
          html.push(`          <strong>${this.escapeHTML(object.name)}</strong> (${object.category}) - 置信度: ${object.confidence.toFixed(2)}`);
          html.push('        </div>');
        });
        html.push('      </div>');
      }

      html.push('    </div>');
    });
    html.push('  </div>');

    html.push('</body>');
    html.push('</html>');
    return html.join('\n');
  }

  /**
   * Ensure output directory exists
   */
  private async ensureOutputDirectory(filePath: string): Promise<void> {
    const dir = path.dirname(filePath);
    try {
      await mkdir(dir, { recursive: true });
    } catch (error) {
      // Directory might already exist
    }
  }

  /**
   * Count occurrences of items in array
   */
  private countOccurrences(items: string[]): Record<string, number> {
    const counts: Record<string, number> = {};
    items.forEach(item => {
      counts[item] = (counts[item] || 0) + 1;
    });
    return counts;
  }

  /**
   * Escape XML special characters
   */
  private escapeXML(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');
  }

  /**
   * Escape HTML special characters
   */
  private escapeHTML(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /**
   * Escape CSV special characters
   */
  private escapeCSV(text: string): string {
    if (text.includes(',') || text.includes('"') || text.includes('\n')) {
      return `"${text.replace(/"/g, '""')}"`;
    }
    return text;
  }
}

/**
 * Convenience function to generate report
 */
export async function generateAnalysisReport(
  videoResults: VideoAnalysisResult[],
  folderMatches: Record<string, FolderMatchResult[]>,
  options: ReportOptions
): Promise<string> {
  const generator = new ReportGenerator();
  return generator.generateReport(videoResults, folderMatches, options);
}
