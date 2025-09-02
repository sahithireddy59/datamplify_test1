import { Injectable } from '@angular/core';
import {  HttpInterceptor,  HttpRequest, HttpResponse, HttpHandler, HttpEvent,  HttpErrorResponse} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { Router } from '@angular/router';
import Swal from 'sweetalert2';
import { AuthService } from './auth.service';
import { environment } from '../../../environments/environment';
@Injectable({
  providedIn: 'root'
})
export class HttpAuthService implements HttpInterceptor {

  constructor(private authService:AuthService) { }
  private isLoggingOut = false; // Flag to prevent multiple logouts

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Attach Authorization header for backend API calls if not already present
    let reqToSend = request;
    try {
      const isApiCall = request.url.startsWith(environment.apiUrl);
      const hasAuth = request.headers.has('Authorization');
      if (isApiCall && !hasAuth) {
        const currentUser = localStorage.getItem('currentUser');
        const token = currentUser ? JSON.parse(currentUser)['Token'] : null;
        if (token) {
          reqToSend = request.clone({
            setHeaders: { Authorization: `Bearer ${token}` }
          });
        }
      }
    } catch { /* ignore token parsing errors */ }

     return next.handle(reqToSend).pipe(
         map((event: HttpEvent<any>) => {
             if (event instanceof HttpResponse) {
                 // console.log('event--->>>', event);
                 // success
             }
             return event;
         }),
         catchError((error: HttpErrorResponse) => {
             let data = {};
             data = {
                 reason: error && error.error.reason ? error.error.reason : '',
                 status: error.status
             };
             if (error.error.message === 'Invalid Access Token' || error.error.message === 'Session Expired, Please login again') {
                if (!this.isLoggingOut) { // Check if already logging out
                    this.isLoggingOut = true; 
                     Swal.fire({
                         icon: 'error',
                         title: 'Oops...',
                         text: 'Session Expired, Please Login!',
                         
                     })

             this.authService.logOut().subscribe(() => {
                this.isLoggingOut = false; // Reset flag after logout
              });;
             }
            }
             return throwError(error);
         }));
}
}
