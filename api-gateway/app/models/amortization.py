# # api-gateway/app/models/amortization.py
# from sqlalchemy import Column, String, ForeignKey, Numeric, Integer, Date, Text, UniqueConstraint
# from sqlalchemy.orm import relationship
# from decimal import Decimal
# from datetime import date, timedelta
# from . import BaseModel

# class Amortization(BaseModel):
#     """Modelo para tablas de amortización"""
#     __tablename__ = "amortizations"
    
#     company_id = Column(String(50), ForeignKey('companies.id'), nullable=False)
#     entity_id = Column(String(36), ForeignKey('entities.id'), nullable=False)
    
#     # Información básica
#     reference = Column(String(100), nullable=False)
#     description = Column(Text)
    
#     # Montos
#     total_amount = Column(Numeric(18, 2), nullable=False)
#     pending_amount = Column(Numeric(18, 2), nullable=False)
#     paid_amount = Column(Numeric(18, 2), default=0)
    
#     # Configuración de cuotas
#     total_installments = Column(Integer, nullable=False)
#     paid_installments = Column(Integer, default=0)
#     installment_amount = Column(Numeric(18, 2), nullable=False)
    
#     # Intereses
#     interest_rate = Column(Numeric(5, 4), default=0)
#     total_interest = Column(Numeric(18, 2), default=0)
    
#     # Fechas
#     start_date = Column(Date, nullable=False)
#     end_date = Column(Date)
#     next_due_date = Column(Date)
    
#     # Estado y configuración
#     status = Column(String(20), default='active')  # active, completed, overdue, suspended, cancelled
#     amortization_method = Column(String(20), default='linear')  # linear, decreasing, french, german
#     frequency = Column(String(20), default='monthly')  # monthly, quarterly, biannual, annual
    
#     # Integración SAP
#     sap_doc_entry = Column(Integer)
#     sap_doc_type = Column(String(10))  # Invoice, Purchase, etc.
#     sap_base_ref = Column(String(50))
    
#     # Campos de control
#     auto_payment = Column(Boolean, default=False)
#     send_notifications = Column(Boolean, default=True)
    
#     # Relaciones
#     company = relationship("Company", back_populates="amortizations")
#     entity = relationship("Entity", back_populates="amortizations")
#     installments = relationship("AmortizationInstallment", back_populates="amortization", 
#                               cascade="all, delete-orphan", order_by="AmortizationInstallment.installment_number")
    
#     def __repr__(self):
#         return f"<Amortization(reference='{self.reference}', total_amount={self.total_amount})>"
    
#     def calculate_installments(self):
#         """Calcular las cuotas de amortización"""
#         installments = []
        
#         if self.amortization_method == 'linear':
#             installments = self._calculate_linear_installments()
#         elif self.amortization_method == 'french':
#             installments = self._calculate_french_installments()
#         elif self.amortization_method == 'german':
#             installments = self._calculate_german_installments()
#         elif self.amortization_method == 'decreasing':
#             installments = self._calculate_decreasing_installments()
        
#         return installments
    
#     def _calculate_linear_installments(self):
#         """Amortización lineal (cuotas iguales de capital)"""
#         installments = []
#         principal_per_installment = self.total_amount / self.total_installments
#         remaining_balance = self.total_amount
        
#         for i in range(self.total_installments):
#             due_date = self._calculate_due_date(i + 1)
#             interest_amount = remaining_balance * (self.interest_rate / 100) / 12
            
#             installment = {
#                 'installment_number': i + 1,
#                 'due_date': due_date,
#                 'principal_amount': principal_per_installment,
#                 'interest_amount': interest_amount,
#                 'total_amount': principal_per_installment + interest_amount,
#                 'remaining_balance': remaining_balance - principal_per_installment
#             }
            
#             installments.append(installment)
#             remaining_balance -= principal_per_installment
        
#         return installments
    
#     def _calculate_french_installments(self):
#         """Sistema francés (cuotas iguales totales)"""
#         installments = []
#         monthly_rate = (self.interest_rate / 100) / 12
        
#         if monthly_rate == 0:
#             # Sin intereses
#             installment_amount = self.total_amount / self.total_installments
#         else:
#             # Con intereses
#             installment_amount = (self.total_amount * monthly_rate * 
#                                 (1 + monthly_rate) ** self.total_installments) / \
#                                ((1 + monthly_rate) ** self.total_installments - 1)
        
#         remaining_balance = self.total_amount
        
#         for i in range(self.total_installments):
#             due_date = self._calculate_due_date(i + 1)
#             interest_amount = remaining_balance * monthly_rate
#             principal_amount = installment_amount - interest_amount
            
#             installment = {
#                 'installment_number': i + 1,
#                 'due_date': due_date,
#                 'principal_amount': principal_amount,
#                 'interest_amount': interest_amount,
#                 'total_amount': installment_amount,
#                 'remaining_balance': remaining_balance - principal_amount
#             }
            
#             installments.append(installment)
#             remaining_balance -= principal_amount
        
#         return installments
    
#     def _calculate_due_date(self, installment_number):
#         """Calcular fecha de vencimiento basada en la frecuencia"""
#         if self.frequency == 'monthly':
#             months = installment_number
#         elif self.frequency == 'quarterly':
#             months = installment_number * 3
#         elif self.frequency == 'biannual':
#             months = installment_number * 6
#         elif self.frequency == 'annual':
#             months = installment_number * 12
#         else:
#             months = installment_number
        
#         # Calcular fecha aproximada (mejorar con dateutil para fechas exactas)
#         return self.start_date + timedelta(days=months * 30)
    
#     def get_status_display(self):
#         """Obtener descripción del estado"""
#         status_map = {
#             'active': 'Activo',
#             'completed': 'Completado',
#             'overdue': 'Vencido',
#             'suspended': 'Suspendido',
#             'cancelled': 'Cancelado'
#         }
#         return status_map.get(self.status, self.status)
    
#     def update_status(self):
#         """Actualizar estado basado en cuotas"""
#         if self.paid_installments >= self.total_installments:
#             self.status = 'completed'
#         elif self.next_due_date and self.next_due_date < date.today():
#             self.status = 'overdue'
#         else:
#             self.status = 'active'
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'company_id': self.company_id,
#             'entity_id': self.entity_id,
#             'reference': self.reference,
#             'description': self.description,
#             'total_amount': float(self.total_amount),
#             'pending_amount': float(self.pending_amount),
#             'paid_amount': float(self.paid_amount),
#             'total_installments': self.total_installments,
#             'paid_installments': self.paid_installments,
#             'installment_amount': float(self.installment_amount),
#             'interest_rate': float(self.interest_rate),
#             'total_interest': float(self.total_interest),
#             'start_date': self.start_date.isoformat() if self.start_date else None,
#             'end_date': self.end_date.isoformat() if self.end_date else None,
#             'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
#             'status': self.status,
#             'status_display': self.get_status_display(),
#             'amortization_method': self.amortization_method,
#             'frequency': self.frequency,
#             'sap_doc_entry': self.sap_doc_entry,
#             'sap_doc_type': self.sap_doc_type,
#             'sap_base_ref': self.sap_base_ref,
#             'auto_payment': self.auto_payment,
#             'send_notifications': self.send_notifications,
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'updated_at': self.updated_at.isoformat() if self.updated_at else None,
#             'is_active': self.is_active
#         }

# class AmortizationInstallment(BaseModel):
#     """Modelo para cuotas de amortización"""
#     __tablename__ = "amortization_installments"
    
#     amortization_id = Column(String(36), ForeignKey('amortizations.id'), nullable=False)
#     installment_number = Column(Integer, nullable=False)
    
#     # Fechas
#     due_date = Column(Date, nullable=False)
#     payment_date = Column(Date)
    
#     # Montos
#     principal_amount = Column(Numeric(18, 2), nullable=False)
#     interest_amount = Column(Numeric(18, 2), default=0)
#     total_amount = Column(Numeric(18, 2), nullable=False)
#     paid_amount = Column(Numeric(18, 2), default=0)
#     remaining_balance = Column(Numeric(18, 2))
    
#     # Estado
#     status = Column(String(20), default='pending')  # pending, paid, overdue, partial
    
#     # Integración SAP
#     sap_payment_entry = Column(Integer)
#     sap_journal_entry = Column(Integer)
    
#     # Información adicional
#     notes = Column(Text)
#     late_fee = Column(Numeric(18, 2), default=0)
    
#     # Relaciones
#     amortization = relationship("Amortization", back_populates="installments")
    
#     __table_args__ = (
#         UniqueConstraint('amortization_id', 'installment_number', name='unique_amortization_installment'),
#     )
    
#     def __repr__(self):
#         return f"<AmortizationInstallment(amortization_id='{self.amortization_id}', number={self.installment_number})>"
    
#     def is_overdue(self):
#         """Verificar si la cuota está vencida"""
#         return self.status == 'pending' and self.due_date < date.today()
    
#     def days_overdue(self):
#         """Días de retraso"""
#         if self.is_overdue():
#             return (date.today() - self.due_date).days
#         return 0
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'amortization_id': self.amortization_id,
#             'installment_number': self.installment_number,
#             'due_date': self.due_date.isoformat() if self.due_date else None,
#             'payment_date': self.payment_date.isoformat() if self.payment_date else None,
#             'principal_amount': float(self.principal_amount),
#             'interest_amount': float(self.interest_amount),
#             'total_amount': float(self.total_amount),
#             'paid_amount': float(self.paid_amount),
#             'remaining_balance': float(self.remaining_balance) if self.remaining_balance else None,
#             'status': self.status,
#             'sap_payment_entry': self.sap_payment_entry,
#             'sap_journal_entry': self.sap_journal_entry,
#             'notes': self.notes,
#             'late_fee': float(self.late_fee),
#             'is_overdue': self.is_overdue(),
#             'days_overdue': self.days_overdue(),
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'updated_at': self.updated_at.isoformat() if self.updated_at else None,
#             'is_active': self.is_active
#         }
# api-gateway/app/models/amortization.py
from sqlalchemy import Column, String, ForeignKey, Numeric, Integer, Date, Text, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from decimal import Decimal
from datetime import date, timedelta
from . import BaseModel

class Amortization(BaseModel):
    """Modelo para tablas de amortización"""
    __tablename__ = "amortizations"
    
    company_id = Column(String(50), ForeignKey('companies.id'), nullable=False)
    entity_id = Column(String(36), ForeignKey('entities.id'), nullable=False)
    
    # Información básica
    reference = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Montos
    total_amount = Column(Numeric(18, 2), nullable=False)
    pending_amount = Column(Numeric(18, 2), nullable=False)
    paid_amount = Column(Numeric(18, 2), default=0)
    
    # Configuración de cuotas
    total_installments = Column(Integer, nullable=False)
    paid_installments = Column(Integer, default=0)
    installment_amount = Column(Numeric(18, 2), nullable=False)
    
    # Intereses
    interest_rate = Column(Numeric(5, 4), default=0)
    total_interest = Column(Numeric(18, 2), default=0)
    
    # Fechas
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    next_due_date = Column(Date)
    
    # Estado y configuración
    status = Column(String(20), default='active')  # active, completed, overdue, suspended, cancelled
    amortization_method = Column(String(20), default='linear')  # linear, decreasing, french, german
    frequency = Column(String(20), default='monthly')  # monthly, quarterly, biannual, annual
    
    # Integración SAP
    sap_doc_entry = Column(Integer)
    sap_doc_type = Column(String(10))  # Invoice, Purchase, etc.
    sap_base_ref = Column(String(50))
    
    # Campos de control
    auto_payment = Column(Boolean, default=False)
    send_notifications = Column(Boolean, default=True)
    
    # Relaciones
    company = relationship("Company", back_populates="amortizations")
    entity = relationship("Entity", back_populates="amortizations")
    installments = relationship("AmortizationInstallment", back_populates="amortization", 
                              cascade="all, delete-orphan", order_by="AmortizationInstallment.installment_number")
    
    def __repr__(self):
        return f"<Amortization(reference='{self.reference}', total_amount={self.total_amount})>"
    
    def calculate_installments(self):
        """Calcular las cuotas de amortización"""
        installments = []
        
        if self.amortization_method == 'linear':
            installments = self._calculate_linear_installments()
        elif self.amortization_method == 'french':
            installments = self._calculate_french_installments()
        elif self.amortization_method == 'german':
            installments = self._calculate_german_installments()
        elif self.amortization_method == 'decreasing':
            installments = self._calculate_decreasing_installments()
        
        return installments
    
    def _calculate_linear_installments(self):
        """Amortización lineal (cuotas iguales de capital)"""
        installments = []
        principal_per_installment = self.total_amount / self.total_installments
        remaining_balance = self.total_amount
        
        for i in range(self.total_installments):
            due_date = self._calculate_due_date(i + 1)
            interest_amount = remaining_balance * (self.interest_rate / 100) / 12
            
            installment = {
                'installment_number': i + 1,
                'due_date': due_date,
                'principal_amount': principal_per_installment,
                'interest_amount': interest_amount,
                'total_amount': principal_per_installment + interest_amount,
                'remaining_balance': remaining_balance - principal_per_installment
            }
            
            installments.append(installment)
            remaining_balance -= principal_per_installment
        
        return installments
    
    def _calculate_french_installments(self):
        """Sistema francés (cuotas iguales totales)"""
        installments = []
        monthly_rate = (self.interest_rate / 100) / 12
        
        if monthly_rate == 0:
            # Sin intereses
            installment_amount = self.total_amount / self.total_installments
        else:
            # Con intereses
            installment_amount = (self.total_amount * monthly_rate * 
                                (1 + monthly_rate) ** self.total_installments) / \
                               ((1 + monthly_rate) ** self.total_installments - 1)
        
        remaining_balance = self.total_amount
        
        for i in range(self.total_installments):
            due_date = self._calculate_due_date(i + 1)
            interest_amount = remaining_balance * monthly_rate
            principal_amount = installment_amount - interest_amount
            
            installment = {
                'installment_number': i + 1,
                'due_date': due_date,
                'principal_amount': principal_amount,
                'interest_amount': interest_amount,
                'total_amount': installment_amount,
                'remaining_balance': remaining_balance - principal_amount
            }
            
            installments.append(installment)
            remaining_balance -= principal_amount
        
        return installments
    
    def _calculate_due_date(self, installment_number):
        """Calcular fecha de vencimiento basada en la frecuencia"""
        if self.frequency == 'monthly':
            months = installment_number
        elif self.frequency == 'quarterly':
            months = installment_number * 3
        elif self.frequency == 'biannual':
            months = installment_number * 6
        elif self.frequency == 'annual':
            months = installment_number * 12
        else:
            months = installment_number
        
        # Calcular fecha aproximada (mejorar con dateutil para fechas exactas)
        return self.start_date + timedelta(days=months * 30)
    
    def get_status_display(self):
        """Obtener descripción del estado"""
        status_map = {
            'active': 'Activo',
            'completed': 'Completado',
            'overdue': 'Vencido',
            'suspended': 'Suspendido',
            'cancelled': 'Cancelado'
        }
        return status_map.get(self.status, self.status)
    
    def update_status(self):
        """Actualizar estado basado en cuotas"""
        if self.paid_installments >= self.total_installments:
            self.status = 'completed'
        elif self.next_due_date and self.next_due_date < date.today():
            self.status = 'overdue'
        else:
            self.status = 'active'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'entity_id': self.entity_id,
            'reference': self.reference,
            'description': self.description,
            'total_amount': float(self.total_amount),
            'pending_amount': float(self.pending_amount),
            'paid_amount': float(self.paid_amount),
            'total_installments': self.total_installments,
            'paid_installments': self.paid_installments,
            'installment_amount': float(self.installment_amount),
            'interest_rate': float(self.interest_rate),
            'total_interest': float(self.total_interest),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
            'status': self.status,
            'status_display': self.get_status_display(),
            'amortization_method': self.amortization_method,
            'frequency': self.frequency,
            'sap_doc_entry': self.sap_doc_entry,
            'sap_doc_type': self.sap_doc_type,
            'sap_base_ref': self.sap_base_ref,
            'auto_payment': self.auto_payment,
            'send_notifications': self.send_notifications,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }

class AmortizationInstallment(BaseModel):
    """Modelo para cuotas de amortización"""
    __tablename__ = "amortization_installments"
    
    amortization_id = Column(String(36), ForeignKey('amortizations.id'), nullable=False)
    installment_number = Column(Integer, nullable=False)
    
    # Fechas
    due_date = Column(Date, nullable=False)
    payment_date = Column(Date)
    
    # Montos
    principal_amount = Column(Numeric(18, 2), nullable=False)
    interest_amount = Column(Numeric(18, 2), default=0)
    total_amount = Column(Numeric(18, 2), nullable=False)
    paid_amount = Column(Numeric(18, 2), default=0)
    remaining_balance = Column(Numeric(18, 2))
    
    # Estado
    status = Column(String(20), default='pending')  # pending, paid, overdue, partial
    
    # Integración SAP
    sap_payment_entry = Column(Integer)
    sap_journal_entry = Column(Integer)
    
    # Información adicional
    notes = Column(Text)
    late_fee = Column(Numeric(18, 2), default=0)
    
    # Relaciones
    amortization = relationship("Amortization", back_populates="installments")
    
    __table_args__ = (
        UniqueConstraint('amortization_id', 'installment_number', name='unique_amortization_installment'),
    )
    
    def __repr__(self):
        return f"<AmortizationInstallment(amortization_id='{self.amortization_id}', number={self.installment_number})>"
    
    def is_overdue(self):
        """Verificar si la cuota está vencida"""
        return self.status == 'pending' and self.due_date < date.today()
    
    def days_overdue(self):
        """Días de retraso"""
        if self.is_overdue():
            return (date.today() - self.due_date).days
        return 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'amortization_id': self.amortization_id,
            'installment_number': self.installment_number,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'principal_amount': float(self.principal_amount),
            'interest_amount': float(self.interest_amount),
            'total_amount': float(self.total_amount),
            'paid_amount': float(self.paid_amount),
            'remaining_balance': float(self.remaining_balance) if self.remaining_balance else None,
            'status': self.status,
            'sap_payment_entry': self.sap_payment_entry,
            'sap_journal_entry': self.sap_journal_entry,
            'notes': self.notes,
            'late_fee': float(self.late_fee),
            'is_overdue': self.is_overdue(),
            'days_overdue': self.days_overdue(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }