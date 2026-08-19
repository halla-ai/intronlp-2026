import { defineCollection, z } from 'astro:content';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

export const collections = {
  docs: defineCollection({
    loader: docsLoader(),
    schema: docsSchema({
      extend: z.object({
        week: z.number().optional(),
        phase: z.number().optional(),
        phase_title: z.string().optional(),
        date: z.string().optional(),
        theory_topics: z.array(z.string()).optional(),
        lab_topics: z.array(z.string()).optional(),
        assignment: z.string().optional(),
        assignment_due: z.string().optional(),
        difficulty: z.enum(['입문', '초급', '중급', '고급', 'beginner', 'elementary', 'intermediate', 'advanced']).optional(),
        estimated_time: z.string().optional(),
      }),
    }),
  }),
};
