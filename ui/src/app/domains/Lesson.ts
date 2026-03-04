export class Lesson {
  id: number = 0
  user_id: number = 0
  course_id: number = 0
  parent_lesson_id: number | null = null
  title: string = ""
  description: string = ""
  text: string = ""
  source_link: string = ""
  tags: string = ""
  created_at: Date = new Date()
}
