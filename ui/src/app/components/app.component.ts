import {Component, OnDestroy, OnInit} from '@angular/core';
import {Link} from "../domains/Link";
import {ActivatedRoute, Router} from "@angular/router";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit, OnDestroy  {

  constructor(private router: Router,
              private route: ActivatedRoute) {
  }

  links: Link[] = [];

  ngOnDestroy(): void {
      console.log("Method not implemented.");
  }

  ngOnInit(): void {
    this.initLinks()
  }

  navigate(navigationPath: string) {
    this.activateCurrentLink(navigationPath);
    this.router.navigate([navigationPath], {relativeTo: this.route});
  }

  private activateCurrentLink(navigationPath?: string) {

    if (navigationPath?.length === 0) {
      navigationPath = 'HOME';
    }

    this.links.forEach(link => {
      link.active = false;

      if (link.name === navigationPath) {
        link.active = true;
      }
    });
  }

  private initLinks() {
    this.addLink("HOME", "house", true, "#0c7e05", "#0bb5ff");
    this.addLink("STATISTICS",  "speedometer2",false, "#ff9520", "#f87a7a");
  }

  private addLink(name: string, icon:string, active: boolean, backgroundColor:string, color: string) {
    let link:Link = new Link();
    link.name = name;
    link.icon = icon;
    link.active = active;
    link.backgroundColor = backgroundColor;
    link.color = color;
    this.links.push(link)
  }


}
