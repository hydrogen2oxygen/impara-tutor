import { Injectable } from '@angular/core';
import {environment} from "../../environments/environment";
import {HttpClient} from "@angular/common/http";
import {User} from "../domains/User";
import {BehaviorSubject, Observable} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class ImparaService {

  baseUrl: string = environment.baseUrl
  private userSubject = new BehaviorSubject<User | null>(null);
  user$ = this.userSubject.asObservable();

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
    this.userSubject.next(user);
    localStorage.setItem("currentUser", JSON.stringify(user))
  }

  logout(): void {
    localStorage.removeItem('currentUser');
    this.userSubject.next(null);
  }
}
