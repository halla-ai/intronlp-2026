// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://intronlp-2026.halla.ai',
  integrations: [
    starlight({
      title: '언어모형과 NLP 2026',
      description: '제주한라대학교 인공지능학과 - 자연어처리 입문. 프로그래밍·수학 배경 없이 시작한다',
      logo: { src: './src/assets/logo.svg' },
      editLink: { baseUrl: 'https://github.com/halla-ai/intronlp-2026/edit/main/' },
      lastUpdated: true,
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/halla-ai/intronlp-2026' },
      ],
      components: { ThemeSelect: './src/components/ThemeSelect.astro' },
      customCss: ['./src/styles/custom.css'],
      sidebar: [
        {
          label: '홈',
          items: [
            { label: '강의 소개', link: '/' },
            { label: '강의계획서', link: '/syllabus' },
            { label: '실습 노트북', link: '/notebooks' },
            { label: '과제 제출', link: '/assignments' },
          ],
        },
        {
          label: '주차별 강의',
          items: [
            { label: '1주차: 자연어처리 소개와 언어모델의 개요', link: '/weeks/week-01' },
            { label: '2주차: 언어와 말뭉치, 텍스트 전처리와 단어 분포', link: '/weeks/week-02' },
            { label: '3주차: 확률론적 언어모델, N-그램 모델', link: '/weeks/week-03' },
            { label: '4주차: 숨겨진 마르코프 모델(HMM)과 시퀀스 태깅', link: '/weeks/week-04' },
            { label: '5주차: 통계적 텍스트 분류, 나이브 베이즈와 문서 분류', link: '/weeks/week-05' },
            { label: '6주차: 단어의 의미 표현, 분포적 통계와 임베딩 기초', link: '/weeks/week-06' },
            { label: '7주차: 신경망 기반 단어 임베딩, Word2Vec', link: '/weeks/week-07' },
            { label: '8주차: 문장 임베딩과 텍스트 유사도', link: '/weeks/week-08' },
            { label: '9주차: 시퀀스 모델링과 트랜스포머의 등장', link: '/weeks/week-09' },
            { label: '10주차: 사전학습 언어모델, BERT와 GPT', link: '/weeks/week-10' },
            { label: '11주차: 대규모 언어모델(LLM)의 시대, 특징과 활용', link: '/weeks/week-11' },
            { label: '12주차: 사전학습 모델 활용법, 프롬프트 엔지니어링', link: '/weeks/week-12' },
            { label: '13주차: NLP 응용 사례 연구 및 최신 동향', link: '/weeks/week-13' },
            { label: '14주차: 언어모델과 사회, 윤리적 이슈와 책임 있는 AI', link: '/weeks/week-14' },
            { label: '15주차: 정리 및 향후 학습 안내', link: '/weeks/week-15' },
          ],
        },
        {
          label: '참고자료',
          collapsed: true,
          items: [
            { label: '데이터 출처', link: '/reference/data' },
          ],
        },
      ],
    }),
  ],
});
