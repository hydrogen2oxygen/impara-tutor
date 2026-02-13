import {Component, OnInit} from '@angular/core';
import {User} from "../../domains/User";
import {FormControl} from "@angular/forms";
import {ImparaService} from "../../services/impara.service";
import {Languages} from "../../domains/Languages";
import {Language} from "../../domains/Language";

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {

  user: User | null = null // synchronized with ImparaService.user$
  userLanguage: Language | null = null // synchronized
  userList: User[] = []
  languages: Languages[] = []
  userLanguages: Language[] = []
  display_name: FormControl = new FormControl('', {nonNullable: true})
  email: FormControl = new FormControl('', {nonNullable: true})
  bio: FormControl = new FormControl('', {nonNullable: true})
  source_language: FormControl = new FormControl('', {nonNullable: true})
  target_language: FormControl = new FormControl('', {nonNullable: true})

  constructor(private imparaService: ImparaService) {
  }

  ngOnInit(): void {
    this.imparaService.listLanguages().subscribe( languages => { this.languages = languages })
    this.imparaService.user$.subscribe( user => {
      this.user = user;
      if (!user) {
        this.imparaService.listUsers().subscribe( users => { this.userList = users })
      } else {
        console.log("also load languages of user")
        this.imparaService.listUserLanguages(user).subscribe(userLanguages => {
          console.log("I'm back")
          this.userLanguages = userLanguages
        })
        console.log("and the current language")
        this.imparaService.language$.subscribe( language => {
          this.userLanguage = language
        })
      }
    })
    let currentUser = localStorage.getItem("currentUser")
    if (currentUser) {
      this.user = JSON.parse(currentUser)
      this.selectUser(this.user)
    } else {
      this.imparaService.listUsers().subscribe( users => { this.userList = users })
    }
  }

  register() {
    this.user = new User()
    this.user.display_name = this.display_name.getRawValue()
    this.user.bio = this.bio.getRawValue()
    this.user.email = this.email.getRawValue()
    this.user.created_at = new Date()
    this.user.last_active_at = new Date()
    this.imparaService.createUser(this.user).subscribe(user => {
      this.imparaService.setUser(user)
    })
  }

  selectUser(user: User | null) {
    this.imparaService.setUser(user)
  }

  protected newLanguage() {

    let language = new Language()
    language.user_id = this.user?.id || 0
    language.source_language = this.source_language.getRawValue()
    language.target_language = this.target_language.getRawValue()

    this.imparaService.createUserLanguage(language).subscribe( language => {
      this.imparaService.setUserLanguage(language)
      this.imparaService.listUserLanguages(this.user).subscribe(userLanguages => {
          this.userLanguages = userLanguages
      })
    })
  }

  protected studyCourse(languageToStudy: Language) {
    this.imparaService.setUserLanguage(languageToStudy)
  }
}
