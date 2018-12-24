import re
import sys
import os
from datetime import datetime
import pandas as pd


FECHA_COMPRA = "FechaCompra"
TIPO_COMPRA = "TipoCompra"
PUNTO_VENTA = "PuntoVenta"
NRO_COMPROBANTE = "NroComprobante"
DESPACHO_IMPORTACION = "DespachoImprentas"
ID_VENDEDOR = "IdVendedor"
RAZON_SOCIAL = "RazonSocial"
IMP_TOTAL_OP = "ImporteTotalOperacion"


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
    return '0' + match[0:4]


def parse_nro_comprobante(nro):
    pattern = re.compile("-[0-9]{8}")
    match = re.search(pattern, nro).group(0)
    return ('0' * 12) + match[1:13]


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


def parse_imp_total_op(total):
    integer, decimal = total.split('.')
    zeros = '0' * (13 - len(integer))
    return zeros + integer + decimal


def parse(cell, coln, feature, register):
    if is_date(cell):
        register[FECHA_COMPRA] = parse_fecha_cpa(cell)
    elif is_comp_tipo(cell):
        register[TIPO_COMPRA] = parse_comp_tipo(cell)
    elif is_nro_comprobante(cell):
        register[PUNTO_VENTA] = parse_pto_venta(cell)
        register[NRO_COMPROBANTE] = parse_nro_comprobante(cell)
        register[DESPACHO_IMPORTACION] = parse_nro_comprobante(cell)
    elif is_cuit(cell):
        register[ID_VENDEDOR] = parse_id_vendedor(cell)
    elif is_razon_social(coln):
        register[RAZON_SOCIAL] = parse_razon_social(cell)
    elif is_total(feature, cell):
        register[IMP_TOTAL_OP] = parse_imp_total_op(cell)


def is_valid_register(register):
    return register.has_key(FECHA_COMPRA)\
           and register.has_key(TIPO_COMPRA)\
           and register.has_key(PUNTO_VENTA)\
           and register.has_key(NRO_COMPROBANTE)\
           and register.has_key(DESPACHO_IMPORTACION)\
           and register.has_key(ID_VENDEDOR)\
           and register.has_key(RAZON_SOCIAL)\
           and register.has_key(IMP_TOTAL_OP)


def print_output(register, output_file):
    output_file.write("{}".format(register[FECHA_COMPRA]))
    output_file.write("{}".format(register[TIPO_COMPRA]))
    output_file.write("{}".format(register[PUNTO_VENTA]))
    output_file.write("{}".format(register[NRO_COMPROBANTE]))
    output_file.write("{}".format(register[DESPACHO_IMPORTACION]))
    output_file.write("80")     # Codigo de documento del vendedor
    output_file.write("{}".format(register[ID_VENDEDOR]))
    output_file.write("{}".format(register[RAZON_SOCIAL]))
    output_file.write("{}".format(register[IMP_TOTAL_OP]))
    output_file.write("000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000PES000100000010000000000000000")
    output_file.write("{}".format(register[FECHA_COMPRA]))
    output_file.write(os.linesep)


def mkdir(output_filename):
    if not os.path.exists(os.path.dirname(output_filename)):
        os.makedirs(os.path.dirname(output_filename))


def transcript(input_directory, filename, output_directory):
    df = load_dataframe(input_directory, filename)
    header = df.head(1)
    output_filename = output_directory + "/" + filename.split('.')[0] + ".txt"
    mkdir(output_filename)
    with open(output_filename, "w") as output_file:
        for index, row in df.iterrows():
            register = {}
            coln = 0
            for feat in header:
                parse(row[feat], coln, feat, register)
                coln += 1
            if is_valid_register(register):
                print_output(register, output_file)


def main():
    input_directory = sys.argv[1] if len(sys.argv) > 1 else 'data'
    output_directory = sys.argv[2] if len(sys.argv) > 2 else 'resultados'
    for filename in sorted(os.listdir(input_directory)):
        if filename.endswith('.csv'):
            transcript(input_directory, filename, output_directory)


if __name__ == '__main__':
    main()

