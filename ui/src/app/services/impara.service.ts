import { Injectable } from '@angular/core';
import {environment} from "../../environments/environment";
import {HttpClient} from "@angular/common/http";
import {User} from "../domains/User";
import {BehaviorSubject, Observable} from "rxjs";
import {Languages} from "../domains/Languages";
import {Language} from "../domains/Language";
import {Course} from "../domains/Course";
import {Lesson} from "../domains/Lesson";
import {DictEntry} from "../domains/DictEntry";
import {DictSense} from "../domains/DictSense";
import {DictTranslation} from "../domains/DictTranslation";
import {DictExample} from "../domains/DictExample";
import {UserSenseState} from "../domains/UserSenseState";

@Injectable({
  providedIn: 'root'
})
export class ImparaService {

  baseUrl: string = environment.baseUrl
  private userSubject = new BehaviorSubject<User | null>(null)
  private languageSubject = new BehaviorSubject<Language | null>(null)
  user$ = this.userSubject.asObservable()
  language$ = this.languageSubject.asObservable()

  constructor(private http: HttpClient) {}

  createUser(user:User):Observable<any> {
    return this.http.post(`${this.baseUrl}api/user`, user)
  }

  uodateUser(user:User):Observable<any> {
    return this.http.put(`${this.baseUrl}api/user`, user)
  }

  listUsers():Observable<User[]> {
    return this.http.get<User[]>(`${this.baseUrl}api/user`)
  }

  deleteUser(userId:string):Observable<any> {
    return this.http.delete(`${this.baseUrl}api/user/${userId}`)
  }

  setUser(user: User | null): void {
    this.userSubject.next(user)
    localStorage.setItem("currentUser", JSON.stringify(user))
  }

  logout(): void {
    localStorage.removeItem('currentUser')
    localStorage.removeItem('currentLanguage')
    this.userSubject.next(null)
    this.languageSubject.next(null)
  }

  listLanguages():Observable<Languages[]> {
    return this.http.get<Languages[]>(`${this.baseUrl}api/languages`)
  }

  createUserLanguage(language:Language):Observable<any> {
    return this.http.post(`${this.baseUrl}api/language`, language)
  }

  listUserLanguages(user: User | null):Observable<Language[]> {
    if (!user) {
      return new Observable<Language[]>()
    }
    return this.http.get<Language[]>(`${this.baseUrl}api/language/${user.id}`)
  }

  setUserLanguage(language:Language):void {
    this.languageSubject.next(language)
    localStorage.setItem("currentLanguage", JSON.stringify(language))
  }

  // ==================== COURSE ENDPOINTS ====================

  listCourses():Observable<Course[]> {
    return this.http.get<Course[]>(`${this.baseUrl}api/courses`)
  }

  listCoursesByUser(userId: number):Observable<Course[]> {
    return this.http.get<Course[]>(`${this.baseUrl}api/courses/user/${userId}`)
  }

  listCoursesByTargetLanguage(targetLanguage: string):Observable<Course[]> {
    return this.http.get<Course[]>(`${this.baseUrl}api/courses/target-language/${targetLanguage}`)
  }

  getCourse(courseId: number):Observable<Course> {
    return this.http.get<Course>(`${this.baseUrl}api/course/${courseId}`)
  }

  createCourse(course:Course):Observable<Course> {
    return this.http.post<Course>(`${this.baseUrl}api/course`, course)
  }

  updateCourse(courseId: number, course:Partial<Course>):Observable<Course> {
    return this.http.put<Course>(`${this.baseUrl}api/course/${courseId}`, course)
  }

  deleteCourse(courseId: number):Observable<any> {
    return this.http.delete(`${this.baseUrl}api/course/${courseId}`)
  }

  // ==================== LESSON ENDPOINTS ====================

  listLessons():Observable<Lesson[]> {
    return this.http.get<Lesson[]>(`${this.baseUrl}api/lessons`)
  }

  listLessonsByUser(userId: number):Observable<Lesson[]> {
    return this.http.get<Lesson[]>(`${this.baseUrl}api/lessons/user/${userId}`)
  }

  listLessonsByCourse(courseId: number):Observable<Lesson[]> {
    return this.http.get<Lesson[]>(`${this.baseUrl}api/lessons/course/${courseId}`)
  }

  listTopLevelLessons(courseId: number):Observable<Lesson[]> {
    return this.http.get<Lesson[]>(`${this.baseUrl}api/lessons/top-level/course/${courseId}`)
  }

  getLesson(lessonId: number):Observable<Lesson> {
    return this.http.get<Lesson>(`${this.baseUrl}api/lesson/${lessonId}`)
  }

  createLesson(lesson:Lesson):Observable<Lesson> {
    return this.http.post<Lesson>(`${this.baseUrl}api/lesson`, lesson)
  }

  updateLesson(lessonId: number, lesson:Partial<Lesson>):Observable<Lesson> {
    return this.http.put<Lesson>(`${this.baseUrl}api/lesson/${lessonId}`, lesson)
  }

  deleteLesson(lessonId: number):Observable<any> {
    return this.http.delete(`${this.baseUrl}api/lesson/${lessonId}`)
  }

  // ==================== DICT_ENTRY ENDPOINTS ====================

  listDictEntries():Observable<DictEntry[]> {
    return this.http.get<DictEntry[]>(`${this.baseUrl}api/dict-entries`)
  }

  listDictEntriesByLanguage(language: string):Observable<DictEntry[]> {
    return this.http.get<DictEntry[]>(`${this.baseUrl}api/dict-entries/language/${language}`)
  }

  getDictEntryByLemma(language: string, lemma: string):Observable<DictEntry> {
    return this.http.get<DictEntry>(`${this.baseUrl}api/dict-entry/lemma/${language}/${lemma}`)
  }

  getDictEntry(entryId: number):Observable<DictEntry> {
    return this.http.get<DictEntry>(`${this.baseUrl}api/dict-entry/${entryId}`)
  }

  createDictEntry(entry:DictEntry):Observable<DictEntry> {
    return this.http.post<DictEntry>(`${this.baseUrl}api/dict-entry`, entry)
  }

  updateDictEntry(entryId: number, entry:Partial<DictEntry>):Observable<DictEntry> {
    return this.http.put<DictEntry>(`${this.baseUrl}api/dict-entry/${entryId}`, entry)
  }

  deleteDictEntry(entryId: number):Observable<any> {
    return this.http.delete(`${this.baseUrl}api/dict-entry/${entryId}`)
  }

  // ==================== DICT_SENSE ENDPOINTS ====================

  listDictSenses():Observable<DictSense[]> {
    return this.http.get<DictSense[]>(`${this.baseUrl}api/dict-senses`)
  }

  listDictSensesByEntry(entryId: number):Observable<DictSense[]> {
    return this.http.get<DictSense[]>(`${this.baseUrl}api/dict-senses/entry/${entryId}`)
  }

  getDictSense(senseId: number):Observable<DictSense> {
    return this.http.get<DictSense>(`${this.baseUrl}api/dict-sense/${senseId}`)
  }

  createDictSense(sense:DictSense):Observable<DictSense> {
    return this.http.post<DictSense>(`${this.baseUrl}api/dict-sense`, sense)
  }

  updateDictSense(senseId: number, sense:Partial<DictSense>):Observable<DictSense> {
    return this.http.put<DictSense>(`${this.baseUrl}api/dict-sense/${senseId}`, sense)
  }

  deleteDictSense(senseId: number):Observable<any> {
    return this.http.delete(`${this.baseUrl}api/dict-sense/${senseId}`)
  }

  // ==================== DICT_TRANSLATION ENDPOINTS ====================

  listDictTranslations():Observable<DictTranslation[]> {
    return this.http.get<DictTranslation[]>(`${this.baseUrl}api/dict-translations`)
  }

  listDictTranslationsBySense(senseId: number):Observable<DictTranslation[]> {
    return this.http.get<DictTranslation[]>(`${this.baseUrl}api/dict-translations/sense/${senseId}`)
  }

  listDictTranslationsByLanguage(targetLanguage: string):Observable<DictTranslation[]> {
    return this.http.get<DictTranslation[]>(`${this.baseUrl}api/dict-translations/language/${targetLanguage}`)
  }

  getDictTranslation(translationId: number):Observable<DictTranslation> {
    return this.http.get<DictTranslation>(`${this.baseUrl}api/dict-translation/${translationId}`)
  }

  createDictTranslation(translation:DictTranslation):Observable<DictTranslation> {
    return this.http.post<DictTranslation>(`${this.baseUrl}api/dict-translation`, translation)
  }

  updateDictTranslation(translationId: number, translation:Partial<DictTranslation>):Observable<DictTranslation> {
    return this.http.put<DictTranslation>(`${this.baseUrl}api/dict-translation/${translationId}`, translation)
  }

  deleteDictTranslation(translationId: number):Observable<any> {
    return this.http.delete(`${this.baseUrl}api/dict-translation/${translationId}`)
  }

  // ==================== DICT_EXAMPLE ENDPOINTS ====================

  listDictExamples():Observable<DictExample[]> {
    return this.http.get<DictExample[]>(`${this.baseUrl}api/dict-examples`)
  }

  listDictExamplesBySense(senseId: number):Observable<DictExample[]> {
    return this.http.get<DictExample[]>(`${this.baseUrl}api/dict-examples/sense/${senseId}`)
  }

  getDictExample(exampleId: number):Observable<DictExample> {
    return this.http.get<DictExample>(`${this.baseUrl}api/dict-example/${exampleId}`)
  }

  createDictExample(example:DictExample):Observable<DictExample> {
    return this.http.post<DictExample>(`${this.baseUrl}api/dict-example`, example)
  }

  updateDictExample(exampleId: number, example:Partial<DictExample>):Observable<DictExample> {
    return this.http.put<DictExample>(`${this.baseUrl}api/dict-example/${exampleId}`, example)
  }

  deleteDictExample(exampleId: number):Observable<any> {
    return this.http.delete(`${this.baseUrl}api/dict-example/${exampleId}`)
  }

  // ==================== USER_SENSE_STATE ENDPOINTS ====================

  listUserSenseStates(userId: number):Observable<UserSenseState[]> {
    return this.http.get<UserSenseState[]>(`${this.baseUrl}api/user-sense-states/user/${userId}`)
  }

  listUserSenseStatesBySense(senseId: number):Observable<UserSenseState[]> {
    return this.http.get<UserSenseState[]>(`${this.baseUrl}api/user-sense-states/sense/${senseId}`)
  }

  getUserSenseState(userId: number, senseId: number):Observable<UserSenseState> {
    return this.http.get<UserSenseState>(`${this.baseUrl}api/user-sense-state/${userId}/${senseId}`)
  }

  createUserSenseState(state:UserSenseState):Observable<UserSenseState> {
    return this.http.post<UserSenseState>(`${this.baseUrl}api/user-sense-state`, state)
  }

  updateUserSenseState(userId: number, senseId: number, state:Partial<UserSenseState>):Observable<UserSenseState> {
    return this.http.put<UserSenseState>(`${this.baseUrl}api/user-sense-state/${userId}/${senseId}`, state)
  }

  deleteUserSenseState(userId: number, senseId: number):Observable<any> {
    return this.http.delete(`${this.baseUrl}api/user-sense-state/${userId}/${senseId}`)
  }
}
