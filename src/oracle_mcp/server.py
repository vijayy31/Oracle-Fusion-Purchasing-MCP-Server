import os, sys
from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError
from oracle_mcp.utils.exception import ConfigurationError
from oracle_mcp.utils.logger import logger
from oracle_mcp.utils.api_call import oracle_get, lifespan

from dotenv import load_dotenv
load_dotenv(override=True)
from datetime import date

mcp = FastMCP(
    "Oracle Fusion Purchasing MCP",
    lifespan=lifespan
)

ORACLE_API_VERSION = "11.13.18.05"

@mcp.tool
async def get_one_purchase_order_details(ctx: Context, po_number: str) -> dict:

    """
        Find a Purchase Order using its Oracle Fusion PO Number

        Args:
            po_number: Purchase Order number to filter by
    
    """
    try:
        logger.info("Tool Calling STARTED: get_one_purchase_order_details")
        po_number = str(po_number).strip() if po_number else None

        if not po_number:
            logger.warning("get_one_purchase_order_details: Argument Missing: po_number cannot be empty")
            raise ToolError(f"Argument po_number cannot be empty. Please provide the valid PO number")
        
        params = {
            "q": f"OrderNumber={po_number}",
            "onlyData": True
        }

        api_version = os.getenv("ORA_API_VERSION") or ORACLE_API_VERSION
        api_endpoint = f"/fscmRestApi/resources/{api_version}/purchaseOrders"

        response = await oracle_get(ctx, endpoint=api_endpoint, params=params, tool_name="get_one_purchase_order_details")

        return response

    finally:
        logger.info("Tool Calling ENDED: get_one_purchase_order_details")


@mcp.tool
async def get_multiple_purchase_orders_details(
    ctx: Context,
    supplier: str | None = None,
    buyer: str | None = None,
    status: str | None = None,
    created_from: date | None = None,
    created_to: date | None = None,
    po_number_starts_with: str | None = None,
    limit: int = 15,
    offset: int = 0,
    sort_order: str = "desc"
 ) -> dict:

    """
    Find multiple Purchase Orders. Search Oracle Fusion purchase orders using optional filters
    Use this tool for requests to list, find or search multiple POs
    If No args are provided simply fetch the request.

    Args: All args are optional
        po_number_starts_with: PO Number starts with to filter by
        supplier: Supplier Name to filter by.
        buyer: Buyer Name to filter by.
        status: Status of the Purchase Order to filter by.
        created_from: Inclusive start date for filtering by creation date. Format: YYYY-MM-DD
        created_to: Inclusive end date for filtering by creation date. Format: YYYY-MM-DD
        limit: Maximum number of results to return. Default is 15. Maximum 50.
        offset: Number of records to skip, default 0
        sort_order: asc or desc, default to desc
    """
    try:
        logger.info("Tool Calling STARTED: get_multiple_purchase_orders_details")

        #Validate pagination
        if limit < 0 or limit > 50:
            logger.warning(f"get_multiple_purchase_orders_details: Argument invalid: Limit should be > 0 or < 50. Current Limit is {limit}")
            raise ToolError(f"Argument invalid: Limit should be > 0 or < 50. Current Limit is {limit}")

        if offset < 0:
            logger.warning(f"get_multiple_purchase_orders_details: Argument invalid: Offset should be > 0. Current Offset is {offset}")
            raise ToolError(f"Argument invalid: Offset should be > 0. Current Offset is {offset}")

        allowed_status = ["open", "closed", "closed for invoicing", "closed for receiving", "cancelled"]
        if status and status.lower() not in allowed_status:
            logger.warning(f"get_multiple_purchase_orders_details: Argument invalid: Status should be one of {', '.join(allowed_status)}")
            raise ToolError(f"Argument invalid: Status should be one of {', '.join(allowed_status)}")

        if sort_order not in ["asc", "desc"]:
            logger.warning(f"get_multiple_purchase_orders_details: Argument invalid: sort_order should be one of asc, desc")
            raise ToolError(f"Argument invalid: sort_order should be one of asc or desc")

        if created_from and created_to and created_from > created_to:
            logger.warning(f"get_multiple_purchase_orders_details: Argument invalid: created_from cannot be after created_to")
            raise ToolError(f"Argument invalid: created_from cannot be after created_to")

        query = ""
        if po_number_starts_with:
            query = query + f"OrderNumber>={po_number_starts_with.upper()}"
        if supplier:
            query= query + f"Supplier={supplier.strip().upper()};"
        if buyer:
            query = query + f"BuyerDisplayName={buyer.strip().title()};"
        if status:
            query = query + f"StatusCode={status.strip().upper()};"
        if created_from:
            query = query + f"CreationDate>={created_from}T00:00:00.000+05:30;"
        if created_to:
            query = query + f"CreationDate<{created_to}T23:59:59.000+05:30;"
        
        if (created_from and created_to) or created_from or po_number_starts_with:
            sort_order="asc"

        params = {
            "limit": limit,
            "onlyData": True,
            "orderBy":f"CreationDate:{sort_order.lower()}",
            "offset": offset,
        }

        if query:
            params["q"] = query

        api_version = os.getenv("ORA_API_VERSION") or ORACLE_API_VERSION
        api_endpoint = f"/fscmRestApi/resources/{api_version}/purchaseOrders"

        response = await oracle_get(ctx, endpoint=api_endpoint, params=params, tool_name="get_multiple_purchase_orders_details")
        
        return response

    finally:
        logger.info("Tool Calling ENDED: get_multiple_purchase_orders_details")


@mcp.tool
async def get_purchase_order_line_details(
    ctx: Context, 
    po_number: str,
    po_header_id: int | None = None,
    limit: int = 20,
    offset: int = 0
    ) -> dict:

    """
        Find a Purchase Order Line Details using its Oracle Fusion PO Number
        Get the line items belonging to an Oracle Fusion purchase order.

        Args:
            po_number: Fusion PO number,
            po_header_id: Unique ID of the PO which is used to retrieve the line details (which is optional)
            limit: Maximum number of lines to return,
            offset: Number of records to skip, default 0

        Note: If both po_number and po_header_id is known, then with po_header_id, LINE details of the PO can be retrieved with single API request
              If there is no po_header_id, First request is to get po_header_id and Second request is to get po LINE details.
    """
    try:
        logger.info("Tool Calling STARTED: get_purchase_order_line_details")
        po_number = str(po_number).strip() if po_number else None

        if not po_number:
            logger.warning("get_purchase_order_line_details: Argument Missing: po_number cannot be empty")
            raise ToolError(f"Argument po_number cannot be empty. Please provide the valid PO number")
        
        if limit < 0 or limit > 100:
            logger.warning(f"get_purchase_order_line_details: Argument invalid: Limit should be > 0 or < 100. Current Limit is {limit}")
            raise ToolError(f"Argument invalid: Limit should be > 0 or < 100. Current Limit is {limit}")

        if offset < 0:
            logger.warning(f"get_purchase_order_line_details: Argument invalid: Offset should be > 0. Current Offset is {offset}")
            raise ToolError(f"Argument invalid: Offset should be > 0. Current Offset is {offset}")
        
        api_version = os.getenv("ORA_API_VERSION") or ORACLE_API_VERSION
        
        if not po_header_id:
            
            po_params = {
                "q": f"OrderNumber={po_number}",
                "onlyData": True
            }
            api_po_endpoint = f"/fscmRestApi/resources/{api_version}/purchaseOrders"
            logger.info("get_purchase_order_line_details: Retrieving po_header_id...")

            po_response = await oracle_get(ctx, endpoint=api_po_endpoint, params=po_params, tool_name="get_purchase_order_line_details")
            items = po_response.get("items",[])

            po_header_id = items[0]["POHeaderId"] if items else None

        if not po_header_id:
            logger.warning("get_purchase_order_line_details: Argument Missing: Unable to retrieve the po_header_id. Check whether the PO number is correct")
            raise ToolError(f"Argument Missing: Unable to retrieve the po_header_id. Check whether the PO number is correct")
        
        api_line_endpoint = f"/fscmRestApi/resources/{api_version}/purchaseOrders/{po_header_id}/child/lines"
        line_params = {
            "onlyData": True,
            "limit": limit,
            "offset": offset
        }
        logger.info("get_purchase_order_line_details: Retrieving PO line details...")
        final_response = await oracle_get(ctx, endpoint=api_line_endpoint, params=line_params, tool_name="get_purchase_order_line_details")
        
        return final_response

    finally:
        logger.info("Tool Calling ENDED: get_purchase_order_line_details")

@mcp.tool
async def get_purchase_order_schedule_details(
    ctx: Context,
    po_number: str,
    limit: int = 20,
    offset: int = 0
    ) -> dict:
    """
        Get Schedule details of the Purchase order

        Args:
            po_number: Purchase Order number,
            limit: Maximum number of schedules to return,
            offset: Number of schedules to skip

        Note: If both po_number and po_header_id is known, then with po_header_id, SCHEDULES details of the PO can be retrieved with single API request
              If there is no po_header_id, First request is to get po_header_id and Second request is to get po SCHEDULES details.
    """
    try:
        logger.info("Tool Calling STARTED: get_purchase_order_schedule_details")
        po_number = str(po_number).strip() if po_number else None

        if not po_number:
            logger.warning("get_purchase_order_schedule_details: Argument Missing: po_number cannot be empty")
            raise ToolError(f"Argument po_number cannot be empty. Please provide the valid PO number")
        
        if limit < 0 or limit > 100:
            logger.warning(f"get_purchase_order_schedule_details: Argument invalid: Limit should be > 0 or < 50. Current Limit is {limit}")
            raise ToolError(f"Argument invalid: Limit should be > 0 or < 100. Current Limit is {limit}")

        if offset < 0:
            logger.warning(f"get_purchase_order_schedule_details: Argument invalid: Offset should be > 0. Current Offset is {offset}")
            raise ToolError(f"Argument invalid: Offset should be > 0. Current Offset is {offset}")
            
        api_version = os.getenv("ORA_API_VERSION") or ORACLE_API_VERSION
        api_endpoint = f"/fscmRestApi/resources/{api_version}/purchaseOrderSchedules"
        
        params = {
            "q": f"OrderNumber={po_number}",
            "onlyData": True,
            "limit": limit,
            "offset": offset
        }
        response = await oracle_get(ctx, endpoint=api_endpoint, params=params, tool_name="get_multiple_purchase_orders")
            
        return response
    
    finally:
        logger.info("Tool Calling ENDED: get_purchase_order_schedule_details")


@mcp.tool
async def get_po_receipt_details(
    ctx:Context,
    po_number: str,
    po_header_id: int | None = None,
    limit: int = 20,
    offset: int = 0
    ) -> dict:
    """
        Get Receipt details for a Purchase Order.

        Args:
            po_number: Fusion PO number,
            po_header_id: Unique ID of the PO which is used to retrieve the PO RECEIPT details (which is optional)
            limit: Maximum number of lines to return,
            offset: Number of records to skip, default 0
        
            Note: If both po_number and po_header_id is known, then with po_header_id, RECEIPT details of the PO can be retrieved with single API request
                  If there is no po_header_id, First request is to get po_header_id and Second request is to get po RECEIPT details.
    """
    try:
        logger.info("Tool Calling STARTED: get_po_receipt_details")
        po_number = str(po_number).strip() if po_number else None

        if not po_number:
            logger.warning("get_po_receipt_details: Argument Missing: po_number cannot be empty")
            raise ToolError(f"Argument po_number cannot be empty. Please provide the valid PO number")
        
        if limit < 0 or limit > 100:
            logger.warning(f"get_po_receipt_details: Argument invalid: Limit should be > 0 or < 100. Current Limit is {limit}")
            raise ToolError(f"Argument invalid: Limit should be > 0 or < 100. Current Limit is {limit}")

        if offset < 0:
            logger.warning(f"get_po_receipt_details: Argument invalid: Offset should be > 0. Current Offset is {offset}")
            raise ToolError(f"Argument invalid: Offset should be > 0. Current Offset is {offset}")
        
        api_version = os.getenv("ORA_API_VERSION") or ORACLE_API_VERSION
        
        if not po_header_id:
            
            po_params = {
                "q": f"OrderNumber={po_number}",
                "onlyData": True
            }
            api_po_endpoint = f"/fscmRestApi/resources/{api_version}/purchaseOrders"
            logger.info("get_po_receipt_details: Retrieving po_header_id...")

            po_response = await oracle_get(ctx, endpoint=api_po_endpoint, params=po_params, tool_name="get_po_receipt_details")
            items = po_response.get("items",[])

            po_header_id = items[0]["POHeaderId"] if items else None

        if not po_header_id:
            logger.warning("get_po_receipt_details: Argument Missing: Unable to retrieve the po_header_id. Check whether the PO number is correct")
            raise ToolError(f"Argument Missing: Unable to retrieve the po_header_id. Check whether the PO number is correct")
        
        api_receipt_endpoint = f"/fscmRestApi/resources/{api_version}/purchaseOrderLifeCycleDetails/{po_header_id}/child/receipts"
        receipt_params = {
            "onlyData": True,
            "limit": limit,
            "offset": offset
        }

        logger.info("get_po_receipt_details: Retrieving PO Receipt details...")
        final_response = await oracle_get(ctx, endpoint=api_receipt_endpoint, params=receipt_params, tool_name="get_po_receipt_details")
        
        return final_response
    
    finally:
         logger.info("Tool Calling ENDED: get_po_receipt_details")


@mcp.tool
async def get_po_invoice_details(
    ctx:Context,
    po_number: str,
    po_header_id: int | None = None,
    limit: int = 20,
    offset: int = 0
    ) -> dict:
    """
        Get Invoice details for a Purchase Order.

        Args:
            po_number: Fusion PO number,
            po_header_id: Unique ID of the PO which is used to retrieve the PO INVOICE details (which is optional)
            limit: Maximum number of lines to return,
            offset: Number of records to skip, default 0
        
            Note: If both po_number and po_header_id is known, then with po_header_id, INVOICE details of the PO can be retrieved with single API request
                  If there is no po_header_id, First request is to get po_header_id and Second request is to get po INVOICE details.
    """
    try:
        logger.info("Tool Calling STARTED: get_po_invoice_details")
        po_number = str(po_number).strip() if po_number else None

        if not po_number:
            logger.warning("get_po_invoice_details: Argument Missing: po_number cannot be empty")
            raise ToolError(f"Argument po_number cannot be empty. Please provide the valid PO number")
        
        if limit < 0 or limit > 100:
            logger.warning(f"get_po_invoice_details: Argument invalid: Limit should be > 0 or < 100. Current Limit is {limit}")
            raise ToolError(f"Argument invalid: Limit should be > 0 or < 100. Current Limit is {limit}")

        if offset < 0:
            logger.warning(f"get_po_invoice_details: Argument invalid: Offset should be > 0. Current Offset is {offset}")
            raise ToolError(f"Argument invalid: Offset should be > 0. Current Offset is {offset}")
        
        api_version = os.getenv("ORA_API_VERSION") or ORACLE_API_VERSION
        
        if not po_header_id:
            
            po_params = {
                "q": f"OrderNumber={po_number}",
                "onlyData": True
            }
            api_po_endpoint = f"/fscmRestApi/resources/{api_version}/purchaseOrders"
            logger.info("get_po_invoice_details: Retrieving po_header_id...")

            po_response = await oracle_get(ctx, endpoint=api_po_endpoint, params=po_params, tool_name="get_po_invoice_details")
            items = po_response.get("items",[])

            po_header_id = items[0]["POHeaderId"] if items else None

        if not po_header_id:
            logger.warning("get_po_invoice_details: Argument Missing: Unable to retrieve the po_header_id. Check whether the PO number is correct")
            raise ToolError(f"Argument Missing: Unable to retrieve the po_header_id. Check whether the PO number is correct")
        
        api_invoice_endpoint = f"/fscmRestApi/resources/{api_version}/purchaseOrderLifeCycleDetails/{po_header_id}/child/invoices"
        invoice_params = {
            "onlyData": True,
            "limit": limit,
            "offset": offset
        }

        logger.info("get_po_invoice_details: Retrieving PO Invoice details...")
        final_response = await oracle_get(ctx, endpoint=api_invoice_endpoint, params=invoice_params, tool_name="get_po_invoice_details")
        
        return final_response
    
    finally:
         logger.info("Tool Calling ENDED: get_po_invoice_details")


@mcp.tool
async def get_po_shipment_details(
    ctx:Context,
    po_number: str,
    po_header_id: int | None = None,
    limit: int = 20,
    offset: int = 0
    ) -> dict:
    """
        Get Shipment details for a Purchase Order.

        Args:
            po_number: Fusion PO number,
            po_header_id: Unique ID of the PO which is used to retrieve the PO SHIPMENT details (which is optional)
            limit: Maximum number of lines to return,
            offset: Number of records to skip, default 0
        
        Note: If both po_number and po_header_id is known, then with po_header_id, SHIPMENT details of the PO can be retrieved with single API request
              If there is no po_header_id, First request is to get po_header_id and Second request is to get po SHIPMENT details.
    """
    try:
        logger.info("Tool Calling STARTED: get_po_shipment_details")
        po_number = str(po_number).strip() if po_number else None

        if not po_number:
            logger.warning("get_po_shipment_details: Argument Missing: po_number cannot be empty")
            raise ToolError(f"Argument po_number cannot be empty. Please provide the valid PO number")
        
        if limit < 0 or limit > 100:
            logger.warning(f"get_po_shipment_details: Argument invalid: Limit should be > 0 or < 100. Current Limit is {limit}")
            raise ToolError(f"Argument invalid: Limit should be > 0 or < 100. Current Limit is {limit}")

        if offset < 0:
            logger.warning(f"get_po_shipment_details: Argument invalid: Offset should be > 0. Current Offset is {offset}")
            raise ToolError(f"Argument invalid: Offset should be > 0. Current Offset is {offset}")
        
        api_version = os.getenv("ORA_API_VERSION") or ORACLE_API_VERSION
        
        if not po_header_id:
            
            po_params = {
                "q": f"OrderNumber={po_number}",
                "onlyData": True
            }
            api_po_endpoint = f"/fscmRestApi/resources/{api_version}/purchaseOrders"
            logger.info("get_po_shipment_details: Retrieving po_header_id...")

            po_response = await oracle_get(ctx, endpoint=api_po_endpoint, params=po_params, tool_name="get_po_shipment_details")
            items = po_response.get("items",[])

            po_header_id = items[0]["POHeaderId"] if items else None

        if not po_header_id:
            logger.warning("get_po_shipment_details: Argument Missing: Unable to retrieve the po_header_id. Check whether the PO number is correct")
            raise ToolError(f"Argument Missing: Unable to retrieve the po_header_id. Check whether the PO number is correct")
        
        api_shipment_endpoint = f"/fscmRestApi/resources/{api_version}/purchaseOrderLifeCycleDetails/{po_header_id}/child/shipments"
        shipment_params = {
            "onlyData": True,
            "limit": limit,
            "offset": offset
        }

        logger.info("get_po_shipment_details: Retrieving PO Invoice details...")
        final_response = await oracle_get(ctx, endpoint=api_shipment_endpoint, params=shipment_params, tool_name="get_po_shipment_details")
        
        return final_response
    
    finally:
         logger.info("Tool Calling ENDED: get_po_shipment_details")


@mcp.tool
async def get_supplier_details(
    ctx: Context,
    supplier_name: str
) -> dict:
    """
        Get the Supplier details from Oracle Fusion

        Args:
            supplier_name: Name of the supplier to be retrieved
    """
    try:
        logger.info("Tool Calling STARTED: get_supplier_details")
        supplier_name = supplier_name.strip() if supplier_name else None

        if not supplier_name:
            logger.warning("get_supplier_details: Argument Missing: supplier_name cannot be empty")
            raise ToolError(f"Argument supplier_name cannot be empty. Please provide the valid Supplier Name")

        api_version = os.getenv("ORA_API_VERSION") or ORACLE_API_VERSION
        api_supplier_endpoint = f"/fscmRestApi/resources/{api_version}/suppliers"

        supplier_params = {
            "q": f"Supplier={supplier_name}",
            "onlyData": True
        }

        logger.info("get_supplier_details: Retrieving Supplier details...")
        response = await oracle_get(ctx, endpoint=api_supplier_endpoint, params=supplier_params, tool_name="get_supplier_details")

        return response
    
    finally:
        logger.info("Tool Calling ENDED: get_supplier_details")


@mcp.tool
async def get_supplier_sites_details(
    ctx: Context,
    supplier_name: str,
    supplier_id: int | None = None,
    limit: int = 20,
    offset: int = 0
) -> dict:
    """
        Get the Supplier details from Oracle Fusion

        Args:
            supplier_name: Name of the supplier to be retrieved
            supplier_id: Unique ID of the SUPPLIER which is used to retrieve the SUPPLIER SITE details (which is optional)
            limit: Maximum number of lines to return,
            offset: Number of records to skip, default 0
    """
    try:
        logger.info("Tool Calling STARTED: get_supplier_details")
        supplier_name = supplier_name.strip() if supplier_name else None

        if not supplier_name:
            logger.warning("get_supplier_sites_details: Argument Missing: supplier_name cannot be empty")
            raise ToolError(f"Argument supplier_name cannot be empty. Please provide the valid Supplier Name")

        api_version = os.getenv("ORA_API_VERSION") or ORACLE_API_VERSION

        if not supplier_id:
            api_supplier_endpoint = f"/fscmRestApi/resources/{api_version}/suppliers"

            supplier_params = {
                "q": f"Supplier={supplier_name}",
                "onlyData": True
            }

            logger.info("get_supplier_sites_details: Retrieving supplier_id...")
            
            supplier_response = await oracle_get(ctx, endpoint=api_supplier_endpoint, params=supplier_params, tool_name="get_supplier_sites_details")
            items = supplier_response.get("items",[])

            supplier_id = items[0]["SupplierId"] if items else None

        if not supplier_id:
            logger.warning("get_supplier_sites_details: Argument Missing: Unable to retrieve the supplier_id. Check whether the Supplier Name is correct")
            raise ToolError(f"Argument Missing: Unable to retrieve the po_header_id. Check whether the Supplier Name is correct")

        api_supplier_sites_endpoint = f"/fscmRestApi/resources/{api_version}/suppliers/{supplier_id}/child/sites"
        
        supplier_sites_params = {
            "onlyData": True,
            "limit": limit,
            "offset": offset
        }

        logger.info("get_supplier_sites_details: Retrieving Supplier Sites details...")
        response = await oracle_get(ctx, endpoint=api_supplier_sites_endpoint, params=supplier_sites_params, tool_name="get_supplier_sites_details")

        return response
    
    finally:
        logger.info("Tool Calling ENDED: get_supplier_sites_details")


@mcp.tool
async def get_one_purchase_agreement_details(ctx: Context, agreement_number: str) -> dict:

    """
        Find a Purchase Agreement using its Oracle Fusion Agreement Number

        Args:
            agreement_number: Agreement Number to filter by
    """
    try:
        logger.info("Tool Calling STARTED: get_one_purchase_agreement_details")
        agreement_number = str(agreement_number).strip() if agreement_number else None

        if not agreement_number:
            logger.warning("get_one_purchase_agreement_details: Argument Missing: agreement_number cannot be empty")
            raise ToolError(f"Argument agreement_number cannot be empty. Please provide the valid agreement number")
        
        params = {
            "q": f"AgreementNumber={agreement_number}",
            "onlyData": True
        }

        api_version = os.getenv("ORA_API_VERSION") or ORACLE_API_VERSION
        api_endpoint = f"/fscmRestApi/resources/{api_version}/purchaseAgreements"

        response = await oracle_get(ctx, endpoint=api_endpoint, params=params, tool_name="get_one_purchase_agreement_details")

        return response

    finally:
        logger.info("Tool Calling ENDED: get_one_purchase_agreement_details")


@mcp.tool
async def get_multiple_purchase_agreement_details(
    ctx: Context,
    supplier: str | None = None,
    buyer: str | None = None,
    status: str | None = None,
    created_from: date | None = None,
    created_to: date | None = None,
    procurement_bu: str | None = None,
    agreement_number_starts_with: str | None = None,
    limit: int = 15,
    offset: int = 0,
    sort_order: str = "desc"
 ) -> dict:

    """
    Find multiple Purchase Agreements. Search Oracle Fusion purchase agreements using optional filters
    Use this tool for requests to list, find or search multiple Agreements
    If No args are provided simply fetch the request.

    Args: All args are optional
        supplier: Supplier Name to filter by.
        buyer: Buyer Name to filter by.
        status: Status of the Agreement to filter by.
        created_from: Inclusive start date for filtering by creation date. Format: YYYY-MM-DD
        created_to: Inclusive end date for filtering by creation date. Format: YYYY-MM-DD
        procurement_bu: Procurement Business Unit to filter by
        agreement_number_starts_with: Agreement Number starts with to filter by
        limit: Maximum number of results to return. Default is 15. Maximum 50.
        offset: Number of records to skip, default 0
        sort_order: asc or desc, default to desc
    """
    try:
        logger.info("Tool Calling STARTED: get_multiple_purchase_agreement_details")

        #Validate pagination
        if limit < 0 or limit > 50:
            logger.warning(f"get_multiple_purchase_agreement_details: Argument invalid: Limit should be > 0 or < 50. Current Limit is {limit}")
            raise ToolError(f"Argument invalid: Limit should be > 0 or < 50. Current Limit is {limit}")

        if offset < 0:
            logger.warning(f"get_multiple_purchase_agreement_details: Argument invalid: Offset should be > 0. Current Offset is {offset}")
            raise ToolError(f"Argument invalid: Offset should be > 0. Current Offset is {offset}")

        allowed_status = ["open", "closed", "cancelled"]
        if status and status.lower() not in allowed_status:
            logger.warning(f"get_multiple_purchase_agreement_details: Argument invalid: Status should be one of {', '.join(allowed_status)}")
            raise ToolError(f"Argument invalid: Status should be one of {', '.join(allowed_status)}")

        if sort_order not in ["asc", "desc"]:
            logger.warning(f"get_multiple_purchase_agreement_details: Argument invalid: sort_order should be one of asc, desc")
            raise ToolError(f"Argument invalid: sort_order should be one of asc or desc")

        if created_from and created_to and created_from > created_to:
            logger.warning(f"get_multiple_purchase_agreement_details: Argument invalid: created_from cannot be after created_to")
            raise ToolError(f"Argument invalid: created_from cannot be greater than created_to")

        query = ""
        if agreement_number_starts_with:
            query = query + f"AgreementNumber>={agreement_number_starts_with.upper()}"
        if supplier:
            query= query + f"Supplier={supplier.strip().upper()};"
        if buyer:
            query = query + f"BuyerFullName={buyer.strip().title()};"
        if status:
            query = query + f"StatusCode={status.strip().upper()};"
        if created_from:
            query = query + f"CreationDate>={created_from}T00:00:00.000+05:30;"
        if created_to:
            query = query + f"CreationDate<{created_to}T23:59:59.000+05:30;"
        if procurement_bu:
            query = query + f"ProcurementBU={procurement_bu}"

        if (created_from and created_to) or created_from or agreement_number_starts_with:
            sort_order="asc"

        params = {
            "limit": limit,
            "onlyData": True,
            "orderBy":f"CreationDate:{sort_order.lower()}",
            "offset": offset,
        }

        if query:
            params["q"] = query

        api_version = os.getenv("ORA_API_VERSION") or ORACLE_API_VERSION
        api_endpoint = f"/fscmRestApi/resources/{api_version}/purchaseAgreements"

        response = await oracle_get(ctx, endpoint=api_endpoint, params=params, tool_name="get_multiple_purchase_agreement_details")
        
        return response

    finally:
        logger.info("Tool Calling ENDED: get_multiple_purchase_agreement_details")


@mcp.tool
async def get_purchase_agreement_lines_details(
    ctx: Context, 
    agreement_number: str,
    agreement_header_id: int | None = None,
    limit: int = 20,
    offset: int = 0
    ) -> dict:

    """
        Find a Purchase Agreement Line Details using its Oracle Fusion Purchase Agreement Number
        Get the line items belonging to an Oracle Fusion purchase Agreement.

        Args:
            agreement_number: Fusion Purchase Agreement number,
            agreement_header_id: Unique ID of the Agreement which is used to retrieve the line details (which is optional)
            limit: Maximum number of lines to return,
            offset: Number of records to skip, default 0

        Note: If both agreement_number and agreement_header_id is known, then with agreement_header_id, LINE details of the Purchase Agreement can be retrieved with single API request
              If there is no agreement_header_id, First request is to get agreement_header_id and Second request is to get Agreement LINE details.
    """
    try:
        logger.info("Tool Calling STARTED: get_purchase_agreement_lines_details")
        agreement_number = str(agreement_number).strip() if agreement_number else None

        if not agreement_number:
            logger.warning("get_purchase_agreement_lines_details: Argument Missing: agreement_number cannot be empty")
            raise ToolError(f"Argument agreement_number cannot be empty. Please provide the valid Agreement number")
        
        if limit < 0 or limit > 200:
            logger.warning(f"get_purchase_agreement_lines_details: Argument invalid: Limit should be > 0 or < 200. Current Limit is {limit}")
            raise ToolError(f"Argument invalid: Limit should be > 0 or < 200. Current Limit is {limit}")

        if offset < 0:
            logger.warning(f"get_purchase_agreement_lines_details: Argument invalid: Offset should be > 0. Current Offset is {offset}")
            raise ToolError(f"Argument invalid: Offset should be > 0. Current Offset is {offset}")
        
        api_version = os.getenv("ORA_API_VERSION") or ORACLE_API_VERSION
        
        if not agreement_header_id:
            
            agreement_params = {
                "q": f"AgreementNumber={agreement_number}",
                "onlyData": True
            }
            api_po_endpoint = f"/fscmRestApi/resources/{api_version}/purchaseAgreements"
            logger.info("get_purchase_agreement_lines_details: Retrieving agreement_header_id...")

            agreement_response = await oracle_get(ctx, endpoint=api_po_endpoint, params=agreement_params, tool_name="get_purchase_agreement_line_details")
            items = agreement_response.get("items",[])

            agreement_header_id = items[0]["AgreementHeaderId"] if items else None

        if not agreement_header_id:
            logger.warning("get_purchase_agreement_lines_details: Argument Missing: Unable to retrieve the agreement_header_id. Check whether the Agreement number is correct")
            raise ToolError(f"Argument Missing: Unable to retrieve the agreement_header_id. Check whether the Agreement number is correct")
        
        api_line_endpoint = f"/fscmRestApi/resources/{api_version}/purchaseAgreements/{agreement_header_id}/child/lines"
        line_params = {
            "onlyData": True,
            "limit": limit,
            "offset": offset
        }
        logger.info("get_purchase_agreement_lines_details: Retrieving Agreement line details...")
        final_response = await oracle_get(ctx, endpoint=api_line_endpoint, params=line_params, tool_name="get_purchase_agreement_line_details")
        
        return final_response

    finally:
        logger.info("Tool Calling ENDED: get_purchase_agreement_lines_details")


def main():
    try:
        logger.info("Starting the Oracle MCP Server...")
        mcp.run(transport = "stdio")

    except ConfigurationError as exc:
        logger.exception(f"Oracle MCP startup failed: Server Stopped. Error: {exc}")
        print(
            f"Oracle MCP startup failed: {exc}",
            file = sys.stderr,
            flush = True
        )
        sys.exit(1)

    except Exception as exc:
        logger.exception(f"Unexpected Error Occurred: {exc}")
        print(
            f"Oracle MCP startup failed: {exc}",
            file = sys.stderr,
            flush = True
        )
        sys.exit(1)

if __name__ == "__main__":
    main()