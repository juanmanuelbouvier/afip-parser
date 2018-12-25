import re
import sys
import os
from datetime import datetime
import pandas as pd


FECHA_COMPRA = "FechaCompra"
TIPO_COMPRA = "TipoCompra"
PUNTO_VENTA = "PuntoVenta"
NRO_COMPROBANTE = "NroComprobante"
ID_VENDEDOR = "IdVendedor"
RAZON_SOCIAL = "RazonSocial"
IMP_TOTAL_OP = "ImporteTotalOperacion"
IMP_NETO_GRAV = "ImporteNetoGravado"
IMP_EX_INT_OT = "ImporteConceptosExIntOt"
IMP_RS_RNI = "ImporteOperacionesExentas"
IMP_PERCEPCIONES = "ImportePercepciones"
IVA = "IVA"


def load_dataframe(directory, filename):
    df = pd.read_csv(directory + '/' + filename)
    return df


def is_date(value):
    try:
        datetime.strptime(value, "%d/%m/%Y")
        return True
    except Exception:
        return False


def parse_fecha_cpa(date):
    return datetime.strptime(date, "%d/%m/%Y").strftime("%Y%m%d")


def is_comp_tipo(value):
    try:
        if value.startswith("FAC"):
            return True
        else:
            return False
    except Exception:
        return False


def parse_comp_tipo(tipo):
    if tipo.endswith("A"):
        return "001"
    elif tipo.endswith("B"):
        return "006"
    elif tipo.endswith("C"):
        return "011"
    else:
        raise Exception("No existe factura de tipo " + tipo)


def is_nro_comprobante(value):
    try:
        pattern = re.compile("[0-9]{4}-")
        if re.match(pattern, value):
            return True
        else:
            return False
    except Exception:
        return False


def parse_pto_venta(nro):
    pattern = re.compile("[0-9]{4}-")
    match = re.match(pattern, nro).group(0)
    return '0' + (match[0:4] if match[0:4] != "0000" else "0001")


def parse_nro_comprobante(nro):
    pattern = re.compile("-[0-9]{8}")
    match = re.search(pattern, nro).group(0)
    return ('0' * 12) + match[1::]


def is_cuit(value):
    try:
        pattern = re.compile("[0-9]{2}-[0-9]{8}-[0-9]")
        if re.match(pattern, value):
            return True
        else:
            return False
    except Exception:
        return False


def parse_id_vendedor(cuit):
    pattern = re.compile("[0-9]{2}-[0-9]{8}-[0-9]")
    match = re.search(pattern, cuit).group(0)
    return ('0' * 9) + match.replace('-', '')


def is_razon_social(coln):
    return coln == 0    # Razon social es la primera columna


def parse_razon_social(razon_social):
    trimmed = ' '.join(razon_social.split())
    whitespaces = ' ' * (30 - len(trimmed.decode('utf-8')))
    return trimmed + whitespaces


def is_total(feature, value):
    try:
        integer, decimal = value.split('.')
        return feature == "Total"
    except Exception:
        return False


def parse_decimal_number(number):
    integer, decimal = number.split('.')
    zeros = '0' * (13 - len(integer))
    return zeros + integer + decimal


def extract_neto(raw):
    split = raw.split(" ")
    if len(split) > 1:
        neto = split[1]
    else:
        neto = split[0]
    return neto


def is_neto_gravado(feature, value):
    try:
        neto = extract_neto(value)
        integer, decimal = neto.split('.')
        return "Neto Gravado" in feature
    except Exception:
        return False


def extract_ex_int_ot(raw):
    split = raw.split(" ")
    return split[0]


def extract_rs_rni(raw):
    split = raw.split(" ")
    if len(split) > 1:
        rs_rni = split[1]
    else:
        rs_rni = split[0]
    return rs_rni


def is_ex_int_ot(feature, value):
    try:
        ex_int_ot = extract_ex_int_ot(value)
        integer, decimal = ex_int_ot.split('.')
        return "Ex/Int/Ot" in feature
    except Exception:
        return False


def is_rs_rni(feature, value):
    try:
        rs_rni = extract_rs_rni(value)
        integer, decimal = rs_rni.split('.')
        return "RS/Rni" in feature
    except Exception:
        return False


def parse_neto_gravado(raw):
    return parse_decimal_number(extract_neto(raw))


def parse_ex_int_ot(raw):
    return parse_decimal_number(extract_ex_int_ot(raw))


def parse_rs_rni(raw):
    return parse_decimal_number(extract_rs_rni(raw))


def is_percepcion(feature, value):
    try:
        integer, decimal = value.split('.')
        return "Percepci" in feature
    except Exception:
        return False


def is_iva(feature, value):
    try:
        integer, decimal = value.split('.')
        return "IVA" in feature
    except Exception:
        return False


def parse(cell, coln, feature, register):
    if is_date(cell):
        register[FECHA_COMPRA] = parse_fecha_cpa(cell)
    elif is_comp_tipo(cell):
        register[TIPO_COMPRA] = parse_comp_tipo(cell)
    elif is_nro_comprobante(cell):
        register[PUNTO_VENTA] = parse_pto_venta(cell)
        register[NRO_COMPROBANTE] = parse_nro_comprobante(cell)
        if is_neto_gravado(feature, cell):  # Tabula puts them in same column
            register[IMP_NETO_GRAV] = parse_neto_gravado(cell)
    elif is_neto_gravado(feature, cell):
        register[IMP_NETO_GRAV] = parse_neto_gravado(cell)
    elif is_ex_int_ot(feature, cell):
        register[IMP_EX_INT_OT] = parse_ex_int_ot(cell)
        if is_rs_rni(feature, cell):        # Tabula puts them in same column
            register[IMP_RS_RNI] = parse_rs_rni(cell)
    elif is_rs_rni(feature, cell):
        register[IMP_RS_RNI] = parse_rs_rni(cell)
    elif is_percepcion(feature, cell):
        register[IMP_PERCEPCIONES] = parse_decimal_number(cell)
    elif is_cuit(cell):
        register[ID_VENDEDOR] = parse_id_vendedor(cell)
    elif is_razon_social(coln):
        register[RAZON_SOCIAL] = parse_razon_social(cell)
    elif is_total(feature, cell):
        register[IMP_TOTAL_OP] = parse_decimal_number(cell)
    elif is_iva(feature, cell):
        register[IVA] = parse_decimal_number(cell)


def is_valid_register(register):
    return register.has_key(FECHA_COMPRA)\
           and register.has_key(TIPO_COMPRA)\
           and register.has_key(PUNTO_VENTA)\
           and register.has_key(NRO_COMPROBANTE)\
           and register.has_key(ID_VENDEDOR)\
           and register.has_key(RAZON_SOCIAL)\
           and register.has_key(IMP_TOTAL_OP)\
           and register.has_key(IMP_NETO_GRAV)\
           and register.has_key(IMP_EX_INT_OT)\
           and register.has_key(IMP_RS_RNI)\
           and register.has_key(IMP_PERCEPCIONES)\
           and register.has_key(IVA)


def print_cbte_output(register, output_file):
    output_file.write("{}".format(register[FECHA_COMPRA]))
    output_file.write("{}".format(register[TIPO_COMPRA]))
    output_file.write("{}".format(register[PUNTO_VENTA]))
    output_file.write("{}".format(register[NRO_COMPROBANTE]))
    output_file.write(" " * 16)     # Despacho de importacion
    output_file.write("80")         # Codigo de documento del vendedor
    output_file.write("{}".format(register[ID_VENDEDOR]))
    output_file.write("{}".format(register[RAZON_SOCIAL]))
    output_file.write("{}".format(register[IMP_TOTAL_OP]))
    output_file.write("{}".format(register[IMP_EX_INT_OT]))
    output_file.write("{}".format(register[IMP_RS_RNI]))
    output_file.write("{}".format(register[IMP_PERCEPCIONES]))
    output_file.write("0" * 15)     # Percepciones o pagos a cuenta de otros impuestos nacionales
    output_file.write("0" * 15)     # Percepciones de IIBB
    output_file.write("0" * 15)     # Percepciones de Impuestos Municipales
    output_file.write("0" * 15)     # Impuestos Internos
    output_file.write("PES")        # Codigo moneda
    output_file.write("0001000000") # Tipo de cambio
    output_file.write("1" if register[TIPO_COMPRA] != "011" else "0")          # Cant alicuotas de IVA
    output_file.write("0")          # Codigo de operacion
    output_file.write("{}".format(register[IVA]))
    output_file.write("0" * 15)     # Otros Tributos
    output_file.write("0" * 11)     # CUIT emisor/corredor
    output_file.write(" " * 30)     # Denominacion del emisor/corredor
    output_file.write("0" * 15)     # IVA comision
    output_file.write("\n")


def print_alicuotas_output(register, output_file):
    output_file.write("{}".format(register[TIPO_COMPRA]))
    output_file.write("{}".format(register[PUNTO_VENTA]))
    output_file.write("{}".format(register[NRO_COMPROBANTE]))
    output_file.write("80")         # Codigo de documento del vendedor
    output_file.write("{}".format(register[ID_VENDEDOR]))
    output_file.write("{}".format(register[IMP_NETO_GRAV]))
    output_file.write("0005")       # Alicuota de IVA (21%)
    output_file.write("{}".format(register[IVA]))
    output_file.write("\n")


def mkdir(output_filename):
    if not os.path.exists(os.path.dirname(output_filename)):
        os.makedirs(os.path.dirname(output_filename))


def transcript(input_directory, filename, output_directory):
    df = load_dataframe(input_directory, filename)
    header = df.head(1)
    cbte_output_filename = output_directory + "/" + "CBTE_" + filename.split('.')[0] + ".txt"
    alicuotas_output_filename = output_directory + "/" + "ALICUOTAS_" + filename.split('.')[0] + ".txt"
    mkdir(cbte_output_filename)
    with open(cbte_output_filename, "w") as cbte_output_file, open(alicuotas_output_filename, "w") as alicuotas_output_file:
        for index, row in df.iterrows():
            register = {}
            coln = 0
            for feat in header:
                parse(row[feat], coln, feat, register)
                coln += 1
            if is_valid_register(register):
                print_cbte_output(register, cbte_output_file)
                print_alicuotas_output(register, alicuotas_output_file)


def main():
    input_directory = sys.argv[1] if len(sys.argv) > 1 else 'data'
    output_directory = sys.argv[2] if len(sys.argv) > 2 else 'resultados'
    for filename in sorted(os.listdir(input_directory)):
        if filename.endswith('.csv'):
            transcript(input_directory, filename, output_directory)


if __name__ == '__main__':
    main()

