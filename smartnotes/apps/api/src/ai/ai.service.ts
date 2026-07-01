import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class AiService {
  private readonly logger = new Logger(AiService.name);
  private readonly apiKey: string | undefined;
  private readonly model = 'gemini-2.0-flash';

  constructor(private readonly configService: ConfigService) {
    this.apiKey = this.configService.get<string>('GEMINI_API_KEY');
    if (!this.apiKey) {
      this.logger.warn(
        'GEMINI_API_KEY not set. AI features will return mock responses.',
      );
    }
  }

  private async callGemini(prompt: string): Promise<string> {
    if (!this.apiKey) {
      // Return mock response when no API key is configured
      return this.getMockResponse(prompt);
    }

    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${this.model}:generateContent?key=${this.apiKey}`;
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: {
            temperature: 0.7,
            maxOutputTokens: 1024,
          },
        }),
      });

      if (!response.ok) {
        const error = await response.text();
        this.logger.error(`Gemini API error: ${error}`);
        throw new Error('AI service unavailable');
      }

      const data = await response.json();
      return data.candidates?.[0]?.content?.parts?.[0]?.text || '';
    } catch (error) {
      this.logger.error('Failed to call Gemini API:', error);
      return this.getMockResponse(prompt);
    }
  }

  private getMockResponse(prompt: string): string {
    if (prompt.includes('Summarize')) {
      return 'This note covers key topics and important ideas. It contains structured content organized into clear sections with actionable items and references.';
    }
    if (prompt.includes('tags')) {
      return JSON.stringify(['productivity', 'ideas', 'planning']);
    }
    if (prompt.includes('suggestions')) {
      return JSON.stringify([
        'Consider adding more specific examples to support your points',
        'You could link this note to related topics for better organization',
        'Try breaking down the larger items into smaller, actionable tasks',
      ]);
    }
    if (prompt.includes('Improve') || prompt.includes('Rewrite')) {
      return 'Here is an improved version of your text with better clarity, structure, and flow. The key points have been preserved while enhancing readability.';
    }
    return 'AI response placeholder';
  }

  async summarize(content: string): Promise<string> {
    const prompt = `Summarize the following note content in 2-3 concise sentences. Focus on the key points and main ideas.\n\nContent:\n${this.stripHtml(content)}`;
    return this.callGemini(prompt);
  }

  async suggestTags(
    content: string,
    existingTags: string[],
  ): Promise<string[]> {
    const prompt = `Analyze the following note content and suggest 3-5 relevant tags for categorization. Return ONLY a JSON array of tag strings, nothing else.\n\nExisting tags in the system: ${existingTags.join(', ')}\n\nContent:\n${this.stripHtml(content)}`;
    const response = await this.callGemini(prompt);
    try {
      // Try to parse as JSON array
      const match = response.match(/\[[\s\S]*?\]/);
      if (match) {
        return JSON.parse(match[0]);
      }
      // Fallback: split by comma
      return response
        .replace(/[\[\]"]/g, '')
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean)
        .slice(0, 5);
    } catch {
      return ['general'];
    }
  }

  async generateSuggestions(content: string): Promise<string[]> {
    const prompt = `Based on the following note content, provide 3 helpful suggestions for the user. These could be: next actions, related ideas to explore, improvements to the content, or organizational tips. Return ONLY a JSON array of suggestion strings.\n\nContent:\n${this.stripHtml(content)}`;
    const response = await this.callGemini(prompt);
    try {
      const match = response.match(/\[[\s\S]*?\]/);
      if (match) {
        return JSON.parse(match[0]);
      }
      return response
        .split('\n')
        .filter((s) => s.trim())
        .slice(0, 3);
    } catch {
      return ['Consider adding more detail to your notes'];
    }
  }

  async improveWriting(content: string): Promise<string> {
    const prompt = `Improve the following text by enhancing clarity, grammar, and flow while preserving the original meaning and intent. Return ONLY the improved text, nothing else.\n\nText:\n${this.stripHtml(content)}`;
    return this.callGemini(prompt);
  }

  private stripHtml(html: string): string {
    return html
      .replace(/<[^>]+>/g, '')
      .replace(/&nbsp;/g, ' ')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .trim();
  }
}
