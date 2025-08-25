from polls.models import Inventory

def refund_sale_item(item, reason=""):
    """Mark a SaleItem as refunded and update inventory."""
    if not item.refunded:
        item.refunded = True
        item.refund_reason = reason
        item.save()

        try:
            inventory = Inventory.objects.get(product=item.product)
            inventory.qty += item.qty
            inventory.save()
        except Inventory.DoesNotExist:
            pass

def refund_whole_sale(sale, reason=""):
    """Refund all items in a sale and mark sale refunded."""
    if sale.refunded:
        return False

    sale.refunded = True
    sale.refund_reason = reason
    sale.save()

    for item in sale.items.all():
        refund_sale_item(item, reason)

    return True