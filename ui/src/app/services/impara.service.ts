import { Injectable } from '@angular/core';
import {environment} from "../../environments/environment";
import {HttpClient} from "@angular/common/http";
import {User} from "../domains/User";
import {BehaviorSubject, Observable} from "rxjs";
import {Languages} from "../domains/Languages";
import {Language} from "../domains/Language";

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
}
