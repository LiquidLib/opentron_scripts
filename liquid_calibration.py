from opentrons import types
from liquidlib.liquids.glycerin import Glycerin
from liquidlib.adapters.opentrons import OpentronsLiquidHandler

metadata = {
    'protocolName': 'Liquid Class Verification',
    'author': 'Hayley McCausland',
}

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.21"
}

########################

def add_parameters(parameters):
    parameters.add_bool(variable_name="wavelength_ref",
                        display_name="Reference Wavelength",
                        description=" ",
                        default=False
                        )
 
def run(ctx):

    global wavelength_ref

    wavelength_ref = ctx.params.wavelength_ref

    #################################

     ## total columns to pipet to in assay plate 
    num_col_assay_plate = 11
    
    ## volume of diluent and reagent to add 
    vol_diluent = 180
    vol_reagent = 20
    liquid = Glycerin()
    print (liquid.to_json())

    # deck layout
    reader = ctx.load_module("absorbanceReaderV1", "D3")

    assay_labware = ctx.load_labware('nest_96_wellplate_200ul_flat', 'A1', 'ASSAY PLATE')
    diluent_labware = ctx.load_labware('axygen_1_reservoir_90ml', 'A2', 'DILUENT RESERVOIR') 
    reagent_labware = ctx.load_labware('nest_12_reservoir_15ml', 'B1', 'REAGENT RESERVOIR')

    ctx.load_trash_bin('A3')

    tips_1000 = ctx.load_labware('opentrons_flex_96_tiprack_1000ul', 'D1', 'P1000 TIPS')
    tips_50 = ctx.load_labware('opentrons_flex_96_tiprack_50ul', 'D2', 'P50 TIPS')

    # pipettes
    left_pipette = ctx.load_instrument(
        "flex_8channel_1000", mount="left", tip_racks=[tips_1000]
    )

    handler_left = OpentronsLiquidHandler(ctx, left_pipette, "./custom_liquid_class_finder/my_liquid_classes.csv")



    # protocol 

    ## add diluent
    for i, col in enumerate(range(2, 13)):  # i goes from 0 to 10
        assay_well = f"A{col}"
        tip_well = f"A{i+1}"  # Starts at A1 for the first transfer

        left_pipette.pick_up_tip(tips_1000[tip_well])               # Pick up a new tip starting from A1
        left_pipette.aspirate(180, diluent_labware["A1"])          # Always aspirate from A1
        left_pipette.dispense(180, assay_labware[assay_well])      # Dispense into A2-A12
        left_pipette.drop_tip()                                  

    ## add reagent and mix
    for i, col in enumerate(range(2, 13)):  # i goes from 0 to 10
        assay_well = f"A{col}"
        tip_well = f"A{i+1}"  # Starts at A1 for the first transfer
        reagent_well = f"A{i+1}"  # Starts at A1 for the first transfer

        left_pipette.pick_up_tip(tips_1000[tip_well])               # Pick up a new tip starting from A1
        handler_left.handle_liquid("Glycerol 99%", 180, reagent_labware[reagent_well], assay_labware[assay_well])
        #left_pipette.aspirate(20, reagent_labware[reagent_well])          # Always aspirate from A1
        #left_pipette.dispense(20, assay_labware[assay_well])      # Dispense into A2-A12
        #left_pipette.mix(5, 25)
        left_pipette.drop_tip()                                  

    ## read plate   
    reader.close_lid()

    if wavelength_ref:
        reader.initialize('single', [562], reference_wavelength=650)      
    else: reader.initialize('single', [562])

    reader.open_lid()
    working_plate = ctx.load_labware('corning_96_wellplate_360ul_flat', 'C2')
    ctx.move_labware(labware = working_plate,
                     new_location = reader,
                     use_gripper=True
                    ) 
    reader.close_lid()
    
    result = reader.read(export_filename="output.csv")

    reader.open_lid()
    ctx.move_labware(labware = working_plate, 
                     new_location = 'C2', 
                     use_gripper=True
                    )
    reader.close_lid()

    ##output data



    