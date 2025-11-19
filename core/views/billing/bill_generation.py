# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Q
import json
from datetime import datetime
from core.models import Bill, Property, BillingCycle, TaxRate

def bill_generation_page(request):
    """Render the main bill generation page"""
    context = {
        'page_title': 'Bill Generation',
        'active_menu': 'billing_generation'
    }
    return render(request, 'core/main/billing/bill-generation.html', context)

def get_bills(request):
    """Get all bills for DataTable"""
    try:
        # Get pagination parameters from DataTables
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        
        # Base queryset
        bills = Bill.objects.select_related(
            'property', 
            'billing_cycle', 
            'created_by'
        ).all()
        
        # Apply search filter
        if search_value:
            bills = bills.filter(
                Q(bill_number__icontains=search_value) |
                Q(property__property_id__icontains=search_value) |
                Q(property__address__icontains=search_value) |
                Q(status__icontains=search_value)
            )
        
        # Get total count
        total_records = bills.count()
        
        # Apply ordering and pagination
        order_column = int(request.GET.get('order[0][column]', 0))
        order_dir = request.GET.get('order[0][dir]', 'asc')
        
        # Map column index to field name
        column_mapping = {
            0: 'id',
            1: 'bill_number',
            2: 'property__property_id',
            3: 'property__address',
            4: 'billing_cycle__name',
            5: 'total_amount',
            6: 'status',
            7: 'generated_date',
            8: 'due_date'
        }
        
        order_field = column_mapping.get(order_column, 'id')
        if order_dir == 'desc':
            order_field = f'-{order_field}'
        
        bills = bills.order_by(order_field)[start:start + length]
        
        # Prepare data for DataTables
        data = []
        for bill in bills:
            # Get primary owner
            primary_owner = bill.property.owners.filter(is_primary_owner=True).first()
            owner_name = primary_owner.owner_name if primary_owner else 'N/A'
            
            data.append({
                'id': bill.id,
                'bill_number': bill.bill_number,
                'property_id': bill.property.property_id,
                'address': bill.property.address,
                'owner_name': owner_name,
                'billing_cycle': bill.billing_cycle.name if bill.billing_cycle else 'N/A',
                'tax_amount': str(bill.tax_amount),
                'penalty_amount': str(bill.penalty_amount),
                'discount_amount': str(bill.discount_amount),
                'total_amount': str(bill.total_amount),
                'status': bill.status,
                'generated_date': bill.generated_date.strftime('%Y-%m-%d %H:%M:%S'),
                'due_date': bill.due_date.strftime('%Y-%m-%d'),
                'created_by': bill.created_by.get_full_name() or bill.created_by.username,
            })
        
        response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': data
        }
        
        return JsonResponse(response)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error fetching bills: {str(e)}'
        }, status=500)

def get_properties_for_billing(request):
    """Get properties that can be billed"""
    try:
        properties = Property.objects.select_related('zone', 'property_type').filter(
            status='active'
        ).prefetch_related('owners')
        
        property_data = []
        for prop in properties:
            primary_owner = prop.owners.filter(is_primary_owner=True).first()
            
            property_data.append({
                'id': prop.id,
                'property_id': prop.property_id,
                'address': prop.address,
                'zone_id': prop.zone.id,
                'zone_name': prop.zone.name if prop.zone else '',
                'property_type_id': prop.property_type.id,
                'property_type_name': prop.property_type.name if prop.property_type else '',
                'assessed_value': str(prop.assessed_value),
                'market_value': str(prop.market_value),
                'total_area': str(prop.total_area),
                'owner_name': primary_owner.owner_name if primary_owner else 'N/A',
                'owner_id': primary_owner.id if primary_owner else None
            })
        
        return JsonResponse({
            'success': True,
            'properties': property_data
        })
        
    except Exception as e:
        print(e)
        return JsonResponse({
            'success': False,
            'error': f'Error fetching properties: {str(e)}'
        }, status=500)

def get_billing_cycles(request):
    """Get active billing cycles"""
    try:
        cycles = BillingCycle.objects.filter(is_active=True)
        
        cycle_data = []
        for cycle in cycles:
            cycle_data.append({
                'id': cycle.id,
                'name': cycle.name,
                'cycle_type': cycle.cycle_type,
                'start_date': cycle.start_date.strftime('%Y-%m-%d'),
                'end_date': cycle.end_date.strftime('%Y-%m-%d'),
                'due_date': cycle.due_date.strftime('%Y-%m-%d')
            })
        
        return JsonResponse({
            'success': True,
            'billing_cycles': cycle_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error fetching billing cycles: {str(e)}'
        }, status=500)

def calculate_tax_amount(request):
    """Calculate tax amount for a property"""
    try:
        data = json.loads(request.body)
        property_id = data.get('property_id')
        billing_cycle_id = data.get('billing_cycle_id')
        
        if not property_id or not billing_cycle_id:
            return JsonResponse({
                'success': False,
                'error': 'Property ID and Billing Cycle ID are required'
            }, status=400)
        
        property_obj = Property.objects.get(id=property_id)
        billing_cycle = BillingCycle.objects.get(id=billing_cycle_id)
        
        # Get current tax rate for the property's zone and type
        current_date = datetime.now().date()
        tax_rate = TaxRate.objects.filter(
            zone=property_obj.zone,
            property_type=property_obj.property_type,
            effective_from__lte=current_date,
            effective_to__gte=current_date
        ).first()
        
        if not tax_rate:
            return JsonResponse({
                'success': False,
                'error': f'No tax rate found for {property_obj.zone.name} - {property_obj.property_type.name}'
            }, status=400)
        
        # Calculate tax amount (assessed_value * tax_rate)
        tax_amount = property_obj.assessed_value * (tax_rate.rate / 100)
        
        return JsonResponse({
            'success': True,
            'tax_amount': str(tax_amount),
            'tax_rate': str(tax_rate.rate),
            'assessed_value': str(property_obj.assessed_value)
        })
        
    except Property.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Property not found'
        }, status=404)
    except BillingCycle.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Billing cycle not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error calculating tax: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_bill(request):
    """Generate a new bill"""
    try:
        with transaction.atomic():
            data = json.loads(request.body)
            
            property_id = data.get('property_id')
            billing_cycle_id = data.get('billing_cycle_id')
            tax_amount = data.get('tax_amount')
            penalty_amount = data.get('penalty_amount', 0)
            discount_amount = data.get('discount_amount', 0)
            notes = data.get('notes', '')
            
            # Validate required fields
            if not all([property_id, billing_cycle_id, tax_amount]):
                return JsonResponse({
                    'success': False,
                    'error': 'Property, billing cycle, and tax amount are required'
                }, status=400)
            
            property_obj = Property.objects.get(id=property_id)
            billing_cycle = BillingCycle.objects.get(id=billing_cycle_id)
            
            # Generate unique bill number
            bill_number = f"BILL-{datetime.now().strftime('%Y%m%d')}-{Bill.objects.count() + 1:06d}"
            
            # Calculate total amount
            total_amount = float(tax_amount) + float(penalty_amount) - float(discount_amount)
            
            # Create bill
            bill = Bill.objects.create(
                bill_number=bill_number,
                property=property_obj,
                billing_cycle=billing_cycle,
                tax_amount=tax_amount,
                penalty_amount=penalty_amount,
                discount_amount=discount_amount,
                total_amount=total_amount,
                status='generated',
                due_date=billing_cycle.due_date,
                created_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Bill {bill_number} generated successfully',
                'bill_id': bill.id,
                'bill_number': bill_number
            })
            
    except Property.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Property not found'
        }, status=404)
    except BillingCycle.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Billing cycle not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error generating bill: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_bill(request, bill_id):
    """Update an existing bill"""
    try:
        with transaction.atomic():
            bill = Bill.objects.get(id=bill_id)
            data = json.loads(request.body)
            
            # Only allow updates to certain fields
            if 'penalty_amount' in data:
                bill.penalty_amount = data['penalty_amount']
            if 'discount_amount' in data:
                bill.discount_amount = data['discount_amount']
            if 'status' in data:
                bill.status = data['status']
            if 'notes' in data:
                bill.notes = data['notes']
            
            # Recalculate total amount
            bill.total_amount = bill.tax_amount + bill.penalty_amount - bill.discount_amount
            bill.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Bill {bill.bill_number} updated successfully'
            })
            
    except Bill.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Bill not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error updating bill: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_bill(request, bill_id):
    """Delete a bill"""
    try:
        bill = Bill.objects.get(id=bill_id)
        bill_number = bill.bill_number
        bill.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Bill {bill_number} deleted successfully'
        })
        
    except Bill.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Bill not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error deleting bill: {str(e)}'
        }, status=500)

def get_bill_details(request, bill_id):
    """Get detailed information about a specific bill"""
    try:
        bill = Bill.objects.select_related(
            'property', 
            'billing_cycle', 
            'created_by'
        ).prefetch_related('property__owners').get(id=bill_id)
        
        primary_owner = bill.property.owners.filter(is_primary_owner=True).first()
        
        bill_data = {
            'id': bill.id,
            'bill_number': bill.bill_number,
            'property': {
                'id': bill.property.id,
                'property_id': bill.property.property_id,
                'address': bill.property.address,
                'zone': bill.property.zone.name,
                'property_type': bill.property.property_type.name,
                'assessed_value': str(bill.property.assessed_value),
                'market_value': str(bill.property.market_value)
            },
            'owner': {
                'name': primary_owner.owner_name if primary_owner else 'N/A',
                'type': primary_owner.owner_type if primary_owner else 'N/A',
                'phone': primary_owner.phone_number if primary_owner else 'N/A'
            },
            'billing_cycle': {
                'name': bill.billing_cycle.name if bill.billing_cycle else 'N/A',
                'cycle_type': bill.billing_cycle.cycle_type if bill.billing_cycle else 'N/A',
                'start_date': bill.billing_cycle.start_date.strftime('%Y-%m-%d') if bill.billing_cycle else 'N/A',
                'end_date': bill.billing_cycle.end_date.strftime('%Y-%m-%d') if bill.billing_cycle else 'N/A',
                'due_date': bill.billing_cycle.due_date.strftime('%Y-%m-%d') if bill.billing_cycle else 'N/A'
            },
            'amounts': {
                'tax_amount': str(bill.tax_amount),
                'penalty_amount': str(bill.penalty_amount),
                'discount_amount': str(bill.discount_amount),
                'total_amount': str(bill.total_amount)
            },
            'status': bill.status,
            'generated_date': bill.generated_date.strftime('%Y-%m-%d %H:%M:%S'),
            'due_date': bill.due_date.strftime('%Y-%m-%d'),
            'created_by': bill.created_by.get_full_name() or bill.created_by.username
        }
        
        return JsonResponse({
            'success': True,
            'bill': bill_data
        })
        
    except Bill.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Bill not found'
        }, status=404)
    except Exception as e:
        print(e)
        return JsonResponse({
            'success': False,
            'error': f'Error fetching bill details: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def bulk_generate_bills(request):
    """Generate bills for multiple properties"""
    try:
        with transaction.atomic():
            data = json.loads(request.body)
            property_ids = data.get('property_ids', [])
            billing_cycle_id = data.get('billing_cycle_id')
            
            if not property_ids or not billing_cycle_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Property IDs and billing cycle are required'
                }, status=400)
            
            billing_cycle = BillingCycle.objects.get(id=billing_cycle_id)
            generated_bills = []
            errors = []
            
            for property_id in property_ids:
                try:
                    property_obj = Property.objects.get(id=property_id)
                    
                    # Calculate tax amount
                    current_date = datetime.now().date()
                    tax_rate = TaxRate.objects.filter(
                        zone=property_obj.zone,
                        property_type=property_obj.property_type,
                        effective_from__lte=current_date,
                        effective_to__gte=current_date
                    ).first()
                    
                    if not tax_rate:
                        errors.append(f'No tax rate found for {property_obj.property_id}')
                        continue
                    
                    tax_amount = property_obj.assessed_value * (tax_rate.rate / 100)
                    
                    # Generate bill number
                    bill_number = f"BILL-{datetime.now().strftime('%Y%m%d')}-{Bill.objects.count() + 1:06d}"
                    
                    # Create bill
                    bill = Bill.objects.create(
                        bill_number=bill_number,
                        property=property_obj,
                        billing_cycle=billing_cycle,
                        tax_amount=tax_amount,
                        penalty_amount=0,
                        discount_amount=0,
                        total_amount=tax_amount,
                        status='generated',
                        due_date=billing_cycle.due_date,
                        created_by=request.user
                    )
                    
                    generated_bills.append(bill_number)
                    
                except Property.DoesNotExist:
                    errors.append(f'Property {property_id} not found')
                except Exception as e:
                    errors.append(f'Error generating bill for property {property_id}: {str(e)}')
            
            return JsonResponse({
                'success': True,
                'message': f'Generated {len(generated_bills)} bills successfully',
                'generated_bills': generated_bills,
                'errors': errors
            })
            
    except BillingCycle.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Billing cycle not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error in bulk bill generation: {str(e)}'
        }, status=500)