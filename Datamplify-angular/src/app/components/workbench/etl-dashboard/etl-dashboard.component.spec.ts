import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EtlDashboardComponent } from './etl-dashboard.component';

describe('EtlDashboardComponent', () => {
  let component: EtlDashboardComponent;
  let fixture: ComponentFixture<EtlDashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EtlDashboardComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(EtlDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
